const pool = require('./db');

class SupabasePgQueryBuilder {
  constructor(table) {
    this.table = table;
    this.type = 'select'; // select, insert, update, delete, upsert
    this.selectedColumns = '*';
    this.selectOptions = {};
    this.insertData = null;
    this.updateData = null;
    this.whereClauses = [];
    this.params = [];
    this.orders = [];
    this.limitVal = null;
    this.offsetVal = null;
    this.isSingle = false;
    this.isMaybeSingle = false;
  }

  select(columns = '*', options = {}) {
    // If called after insert or update, it indicates RETURNING *
    if (this.type === 'select') {
      this.selectedColumns = columns;
      this.selectOptions = options;
    }
    return this;
  }

  insert(data) {
    this.type = 'insert';
    this.insertData = Array.isArray(data) ? data : [data];
    return this;
  }

  update(data) {
    this.type = 'update';
    this.updateData = data;
    return this;
  }

  delete() {
    this.type = 'delete';
    return this;
  }

  upsert(data, options = {}) {
    this.type = 'upsert';
    this.insertData = Array.isArray(data) ? data : [data];
    this.upsertOptions = options;
    return this;
  }

  eq(col, val) {
    if (val === null || val === undefined) {
      this.whereClauses.push(`"${col}" IS NULL`);
    } else {
      this.params.push(val);
      this.whereClauses.push(`"${col}" = $${this.params.length}`);
    }
    return this;
  }

  neq(col, val) {
    this.params.push(val);
    this.whereClauses.push(`"${col}" != $${this.params.length}`);
    return this;
  }

  gt(col, val) {
    this.params.push(val);
    this.whereClauses.push(`"${col}" > $${this.params.length}`);
    return this;
  }

  gte(col, val) {
    this.params.push(val);
    this.whereClauses.push(`"${col}" >= $${this.params.length}`);
    return this;
  }

  lt(col, val) {
    this.params.push(val);
    this.whereClauses.push(`"${col}" < $${this.params.length}`);
    return this;
  }

  lte(col, val) {
    this.params.push(val);
    this.whereClauses.push(`"${col}" <= $${this.params.length}`);
    return this;
  }

  in(col, arr) {
    if (!Array.isArray(arr) || arr.length === 0) {
      this.whereClauses.push('1 = 0');
      return this;
    }
    const placeholders = arr.map(v => {
      this.params.push(v);
      return `$${this.params.length}`;
    });
    this.whereClauses.push(`"${col}" IN (${placeholders.join(', ')})`);
    return this;
  }

  ilike(col, pattern) {
    this.params.push(pattern);
    this.whereClauses.push(`"${col}" ILIKE $${this.params.length}`);
    return this;
  }

  like(col, pattern) {
    this.params.push(pattern);
    this.whereClauses.push(`"${col}" LIKE $${this.params.length}`);
    return this;
  }

  is(col, val) {
    if (val === null) {
      this.whereClauses.push(`"${col}" IS NULL`);
    } else {
      this.params.push(val);
      this.whereClauses.push(`"${col}" IS $${this.params.length}`);
    }
    return this;
  }

  or(expr) {
    if (expr.includes('status.eq.PUBLISHED,status.is.null')) {
      this.whereClauses.push('("status" = \'PUBLISHED\' OR "status" IS NULL)');
    } else {
      const parts = expr.split(',').map(p => {
        const segs = p.split('.');
        const col = segs[0];
        const op = segs[1];
        const val = segs[2];
        if (op === 'eq') return `"${col}" = '${val}'`;
        if (op === 'is' && val === 'null') return `"${col}" IS NULL`;
        return '1=1';
      });
      this.whereClauses.push(`(${parts.join(' OR ')})`);
    }
    return this;
  }

  order(col, options = { ascending: true }) {
    const dir = options.ascending === false ? 'DESC' : 'ASC';
    this.orders.push(`"${col}" ${dir}`);
    return this;
  }

  limit(n) {
    this.limitVal = n;
    return this;
  }

  range(from, to) {
    this.offsetVal = from;
    this.limitVal = to - from + 1;
    return this;
  }

  single() {
    this.isSingle = true;
    return this;
  }

  maybeSingle() {
    this.isMaybeSingle = true;
    return this;
  }

  async execute() {
    try {
      const wherePart = this.whereClauses.length > 0 ? `WHERE ${this.whereClauses.join(' AND ')}` : '';

      // Count only query if { count: 'exact', head: true }
      if (this.selectOptions && this.selectOptions.count === 'exact' && this.selectOptions.head) {
        const countSql = `SELECT count(*)::int AS count FROM "${this.table}" ${wherePart}`;
        const countRes = await pool.query(countSql, this.params);
        return { data: null, count: countRes.rows[0].count, error: null };
      }

      let count = null;
      if (this.selectOptions && this.selectOptions.count === 'exact') {
        const countSql = `SELECT count(*)::int AS count FROM "${this.table}" ${wherePart}`;
        const countRes = await pool.query(countSql, this.params);
        count = countRes.rows[0].count;
      }

      if (this.type === 'select') {
        let sql = `SELECT * FROM "${this.table}" ${wherePart}`;
        if (this.orders.length > 0) sql += ` ORDER BY ${this.orders.join(', ')}`;
        if (this.limitVal !== null) sql += ` LIMIT ${this.limitVal}`;
        if (this.offsetVal !== null) sql += ` OFFSET ${this.offsetVal}`;

        const res = await pool.query(sql, this.params);
        let rows = res.rows;

        // Foreign relations population
        if (this.selectedColumns && this.selectedColumns.includes('profiles')) {
          const userIds = rows.map(r => r.id || r.user_id).filter(Boolean);
          if (userIds.length > 0) {
            const profRes = await pool.query(`SELECT * FROM profiles WHERE user_id = ANY($1)`, [userIds]);
            const profMap = {};
            profRes.rows.forEach(p => { profMap[p.user_id] = p; });
            rows = rows.map(r => ({ ...r, profiles: profMap[r.id || r.user_id] || null }));
          }
        }
        if (this.selectedColumns && this.selectedColumns.includes('categories')) {
          const catIds = [...new Set(rows.map(r => r.category_id).filter(Boolean))];
          if (catIds.length > 0) {
            const catRes = await pool.query(`SELECT * FROM categories WHERE id = ANY($1)`, [catIds]);
            const catMap = {};
            catRes.rows.forEach(c => { catMap[c.id] = c; });
            rows = rows.map(r => ({ ...r, categories: catMap[r.category_id] || null }));
          }
        }
        if (this.selectedColumns && this.selectedColumns.includes('orders')) {
          const orderIds = [...new Set(rows.map(r => r.order_id).filter(Boolean))];
          if (orderIds.length > 0) {
            const ordRes = await pool.query(`SELECT * FROM orders WHERE id = ANY($1)`, [orderIds]);
            const ordMap = {};
            ordRes.rows.forEach(o => { ordMap[o.id] = o; });
            rows = rows.map(r => ({ ...r, orders: ordMap[r.order_id] || null }));
          }
        }
        if (this.selectedColumns && this.selectedColumns.includes('delivery_agents')) {
          const agentIds = [...new Set(rows.map(r => r.agent_id).filter(Boolean))];
          if (agentIds.length > 0) {
            const agRes = await pool.query(`SELECT * FROM delivery_agents WHERE id = ANY($1)`, [agentIds]);
            const agMap = {};
            agRes.rows.forEach(a => { agMap[a.id] = a; });
            rows = rows.map(r => ({ ...r, delivery_agents: agMap[r.agent_id] || null }));
          }
        }
        if (this.selectedColumns && this.selectedColumns.includes('cycle_settings')) {
          const userIds = rows.map(r => r.id).filter(Boolean);
          if (userIds.length > 0) {
            const csRes = await pool.query(`SELECT * FROM cycle_settings WHERE user_id = ANY($1)`, [userIds]);
            const csMap = {};
            csRes.rows.forEach(c => { csMap[c.user_id] = c; });
            rows = rows.map(r => ({ ...r, cycle_settings: csMap[r.id] || null }));
          }
        }

        if (this.isSingle) {
          if (rows.length === 0) return { data: null, error: { message: 'Row not found', code: 'PGRST116' }, count };
          return { data: rows[0], error: null, count };
        }
        if (this.isMaybeSingle) {
          return { data: rows.length > 0 ? rows[0] : null, error: null, count };
        }
        return { data: rows, error: null, count };
      }

      if (this.type === 'insert') {
        const rows = this.insertData;
        if (!rows || rows.length === 0) return { data: [], error: null };
        const inserted = [];
        for (const item of rows) {
          const keys = Object.keys(item);
          const cols = keys.map(k => `"${k}"`).join(', ');
          const placeholders = keys.map((_, i) => `$${i + 1}`).join(', ');
          const vals = keys.map(k => item[k]);
          const sql = `INSERT INTO "${this.table}" (${cols}) VALUES (${placeholders}) RETURNING *`;
          const res = await pool.query(sql, vals);
          inserted.push(res.rows[0]);
        }
        if (this.isSingle) {
          return { data: inserted[0] || null, error: null };
        }
        return { data: inserted, error: null };
      }

      if (this.type === 'update') {
        const keys = Object.keys(this.updateData);
        if (keys.length === 0) return { data: [], error: null };
        const setClauses = [];
        const vals = [];
        keys.forEach((k, idx) => {
          vals.push(this.updateData[k]);
          setClauses.push(`"${k}" = $${idx + 1}`);
        });

        const offset = vals.length;
        const shiftedWhere = this.whereClauses.map(clause => {
          return clause.replace(/\$(\d+)/g, (_, num) => `$${parseInt(num) + offset}`);
        });
        const fullParams = vals.concat(this.params);
        const whereSql = shiftedWhere.length > 0 ? `WHERE ${shiftedWhere.join(' AND ')}` : '';

        const sql = `UPDATE "${this.table}" SET ${setClauses.join(', ')} ${whereSql} RETURNING *`;
        const res = await pool.query(sql, fullParams);
        if (this.isSingle) {
          return { data: res.rows[0] || null, error: null };
        }
        return { data: res.rows, error: null };
      }

      if (this.type === 'delete') {
        const sql = `DELETE FROM "${this.table}" ${wherePart} RETURNING *`;
        const res = await pool.query(sql, this.params);
        return { data: res.rows, error: null };
      }

      if (this.type === 'upsert') {
        const rows = this.insertData;
        const inserted = [];
        const conflictTarget = this.upsertOptions?.onConflict || 'id';
        for (const item of rows) {
          const keys = Object.keys(item);
          const cols = keys.map(k => `"${k}"`).join(', ');
          const placeholders = keys.map((_, i) => `$${i + 1}`).join(', ');
          const vals = keys.map(k => item[k]);
          const updateSet = keys.filter(k => k !== conflictTarget).map(k => `"${k}" = EXCLUDED."${k}"`).join(', ');
          const sql = `INSERT INTO "${this.table}" (${cols}) VALUES (${placeholders}) ON CONFLICT ("${conflictTarget}") DO UPDATE SET ${updateSet} RETURNING *`;
          const res = await pool.query(sql, vals);
          inserted.push(res.rows[0]);
        }
        return { data: this.isSingle ? inserted[0] : inserted, error: null };
      }

      return { data: null, error: { message: 'Unsupported operation' } };
    } catch (err) {
      console.error('SupabasePgAdapter Query Error:', err.message);
      return { data: null, error: { message: err.message } };
    }
  }

  then(onFulfilled, onRejected) {
    return this.execute().then(onFulfilled, onRejected);
  }
}

const supabase = {
  from(table) {
    return new SupabasePgQueryBuilder(table);
  }
};

module.exports = supabase;
