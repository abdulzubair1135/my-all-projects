const supabase = require('../config/supabase');

const getArticles = async (req, res, next) => {
  try {
    const { category_id } = req.query;
    let query = supabase.from('wellness_articles').select('*, wellness_categories(name)').eq('status', 'PUBLISHED');

    if (category_id) query = query.eq('category_id', category_id);

    const { data, error } = await query.order('created_at', { ascending: false });
    if (error) throw error;

    res.json({ success: true, articles: data });
  } catch (err) {
    next(err);
  }
};

const getCategories = async (req, res, next) => {
  try {
    const { data, error } = await supabase.from('wellness_categories').select('*').order('name');
    if (error) throw error;

    res.json({ success: true, categories: data });
  } catch (err) {
    next(err);
  }
};

const getArticleById = async (req, res, next) => {
  try {
    const articleId = req.params.id;
    const { data, error } = await supabase
      .from('wellness_articles')
      .select('*, wellness_categories(name)')
      .eq('id', articleId)
      .single();

    if (error || !data) return res.status(404).json({ success: false, message: 'Article not found' });
    res.json({ success: true, article: data });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  getArticles,
  getCategories,
  getArticleById
};
