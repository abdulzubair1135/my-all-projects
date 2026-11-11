/**
 * Relationship Mapping Service for CycleCare
 * Centralized, bidirectional, perspective-aware relationship mapping.
 *
 * Implements:
 * - Canonical tag normalization (strips emoji, aliases, whitespace)
 * - Automatic reciprocal determination based on actor and target profiles
 * - Ambiguity detection and option generation
 * - Relationship pairing compatibility validation
 */

const CANONICAL_RELATIONSHIPS = [
  'Husband',
  'Wife',
  'Boyfriend',
  'Girlfriend',
  'Father',
  'Mother',
  'Daughter',
  'Son',
  'Brother',
  'Sister',
  'Best Friend',
  'Family',
  'Guardian',
  'Partner',
  'Other'
];

const COMPATIBILITY_RULES = {
  'Husband': ['Wife', 'Husband', 'Partner'],
  'Wife': ['Husband', 'Wife', 'Partner'],
  'Boyfriend': ['Girlfriend', 'Boyfriend', 'Partner'],
  'Girlfriend': ['Boyfriend', 'Girlfriend', 'Partner'],
  'Father': ['Daughter', 'Son', 'Family', 'Other'],
  'Mother': ['Daughter', 'Son', 'Family', 'Other'],
  'Daughter': ['Father', 'Mother', 'Family', 'Other'],
  'Son': ['Father', 'Mother', 'Family', 'Other'],
  'Brother': ['Sister', 'Brother', 'Family', 'Other'],
  'Sister': ['Brother', 'Sister', 'Family', 'Other'],
  'Best Friend': ['Best Friend', 'Family', 'Partner', 'Other'],
  'Partner': ['Partner', 'Husband', 'Wife', 'Boyfriend', 'Girlfriend', 'Other'],
  'Family': ['Family', 'Father', 'Mother', 'Daughter', 'Son', 'Brother', 'Sister', 'Guardian', 'Other'],
  'Guardian': ['Daughter', 'Son', 'Family', 'Other'],
  'Other': ['Other', 'Family', 'Best Friend', 'Partner', 'Husband', 'Wife']
};

/**
 * Normalizes any raw tag string to a canonical relationship tag.
 * Strips emoji, whitespace, and resolves common synonyms.
 *
 * @param {string} rawTag
 * @returns {string} Canonical relationship tag
 */
function normalizeRelationshipTag(rawTag) {
  if (!rawTag || typeof rawTag !== 'string') return 'Other';

  // Strip emoji and extraneous punctuation
  const cleaned = rawTag
    .replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE00}-\u{FE0F}]/gu, '')
    .trim();

  const lower = cleaned.toLowerCase();

  if (lower.includes('husband') || lower === 'hubby' || lower === 'pati') return 'Husband';
  if (lower.includes('wife') || lower === 'wifey' || lower === 'patni') return 'Wife';
  if (lower.includes('boyfriend') || lower === 'bf') return 'Boyfriend';
  if (lower.includes('girlfriend') || lower === 'gf') return 'Girlfriend';
  if (lower.includes('father') || lower.includes('dad') || lower === 'papa' || lower === 'daddy') return 'Father';
  if (lower.includes('mother') || lower.includes('mom') || lower === 'mum' || lower === 'mummy' || lower === 'maa') return 'Mother';
  if (lower.includes('daughter') || lower === 'beti') return 'Daughter';
  if (lower.includes('son') || lower === 'beta') return 'Son';
  if (lower.includes('brother') || lower === 'bro' || lower === 'bhai') return 'Brother';
  if (lower.includes('sister') || lower === 'sis' || lower === 'behen' || lower === 'didi') return 'Sister';
  if (lower.includes('best friend') || lower.includes('bestie') || lower === 'bfft' || lower.includes('friend')) return 'Best Friend';
  if (lower.includes('guardian')) return 'Guardian';
  if (lower.includes('partner') || lower === 'spouse') return 'Partner';
  if (lower.includes('family') || lower.includes('relative') || lower.includes('parent')) return 'Family';

  // Check exact canonical case-insensitive match
  for (const canonical of CANONICAL_RELATIONSHIPS) {
    if (canonical.toLowerCase() === lower) return canonical;
  }

  return 'Other';
}

/**
 * Checks whether an assigned tag and a proposed reciprocal tag are logically compatible.
 *
 * @param {string} assignedTag
 * @param {string} reciprocalTag
 * @returns {{ valid: boolean, reason?: string }}
 */
function validateCompatibility(assignedTag, reciprocalTag) {
  const normAssigned = normalizeRelationshipTag(assignedTag);
  const normReciprocal = normalizeRelationshipTag(reciprocalTag);

  const allowedReciprocals = COMPATIBILITY_RULES[normAssigned];
  if (!allowedReciprocals) {
    return { valid: true };
  }

  if (allowedReciprocals.includes(normReciprocal)) {
    return { valid: true };
  }

  return {
    valid: false,
    reason: `Incompatible relationship pairing: ${normAssigned} cannot be reciprocated as ${normReciprocal}.`
  };
}

/**
 * Returns possible ambiguity options for a relationship if the actor's gender cannot be inferred.
 *
 * @param {string} assignedTag
 * @returns {string[]}
 */
function getAmbiguityOptions(assignedTag) {
  const norm = normalizeRelationshipTag(assignedTag);
  switch (norm) {
    case 'Father':
    case 'Mother':
      return ['Daughter', 'Son'];
    case 'Daughter':
    case 'Son':
      return ['Mother', 'Father'];
    case 'Brother':
    case 'Sister':
      return ['Sister', 'Brother'];
    case 'Husband':
    case 'Wife':
      return ['Wife', 'Husband'];
    case 'Boyfriend':
    case 'Girlfriend':
      return ['Girlfriend', 'Boyfriend'];
    default:
      return [];
  }
}

/**
 * Resolves effective gender from profile gender or usage mode.
 *
 * @param {string} gender
 * @param {string} usageMode
 * @returns {'FEMALE'|'MALE'|null}
 */
function resolveEffectiveGender(gender, usageMode) {
  if (gender && typeof gender === 'string') {
    const g = gender.toUpperCase().trim();
    if (g === 'FEMALE' || g === 'F' || g === 'WOMAN') return 'FEMALE';
    if (g === 'MALE' || g === 'M' || g === 'MAN') return 'MALE';
  }

  if (usageMode && typeof usageMode === 'string') {
    const mode = usageMode.toUpperCase().trim();
    if (mode === 'TRACK_CYCLE') return 'FEMALE';
    if (mode === 'SUPPORT_PARTNER' || mode === 'PARTNER') return 'MALE';
  }

  return null;
}

/**
 * Centralized reciprocal determination engine.
 *
 * When User A (Actor) tags User B (Target) as `assignedTag`:
 * - User A views User B as `assignedTag`.
 * - User B views User A as the calculated `reciprocal`.
 *
 * @param {Object} params
 * @param {string} params.assignedTag - Relationship tag assigned by Actor A for Target B
 * @param {string} [params.actorGender] - Gender of Actor A
 * @param {string} [params.actorUsageMode] - Usage mode of Actor A ('TRACK_CYCLE', 'SUPPORT_PARTNER', etc.)
 * @param {string} [params.targetGender] - Gender of Target B
 * @param {string} [params.targetUsageMode] - Usage mode of Target B
 * @param {string} [params.explicitReciprocal] - Optional explicit reciprocal tag specified by user
 * @param {boolean} [params.strictAmbiguity=false] - If true, throws/fails when ambiguous rather than using default
 *
 * @returns {{
 *   assigned: string,
 *   reciprocal: string,
 *   isAmbiguous: boolean,
 *   ambiguityOptions: string[],
 *   determinedBy: 'EXPLICIT'|'INFERRED'|'DEFAULT'
 * }}
 */
function determineReciprocal(params) {
  const {
    assignedTag,
    actorGender,
    actorUsageMode,
    targetGender,
    targetUsageMode,
    explicitReciprocal,
    strictAmbiguity = false
  } = params || {};

  const normAssigned = normalizeRelationshipTag(assignedTag);

  // 1. Explicit reciprocal provided
  if (explicitReciprocal) {
    const normExplicit = normalizeRelationshipTag(explicitReciprocal);
    const isAsymmetric = ['Husband', 'Wife', 'Father', 'Mother', 'Daughter', 'Son'].includes(normAssigned);
    if (!isAsymmetric || normExplicit !== normAssigned) {
      const compatCheck = validateCompatibility(normAssigned, normExplicit);
      if (!compatCheck.valid) {
        const err = new Error(compatCheck.reason);
        err.code = 'INCOMPATIBLE_RELATIONSHIP';
        err.statusCode = 400;
        throw err;
      }
      return {
        assigned: normAssigned,
        reciprocal: normExplicit,
        isAmbiguous: false,
        ambiguityOptions: [],
        determinedBy: 'EXPLICIT'
      };
    }
  }

  const effectiveActorGender = resolveEffectiveGender(actorGender, actorUsageMode);
  let reciprocal = null;
  let isAmbiguous = false;
  let determinedBy = 'INFERRED';

  switch (normAssigned) {
    case 'Husband':
      // Actor tags Target as Husband -> Target is Husband.
      // Actor is Wife (if female or TRACK_CYCLE or default) or Husband (if male).
      if (effectiveActorGender === 'MALE') {
        reciprocal = 'Husband';
      } else {
        reciprocal = 'Wife';
      }
      break;

    case 'Wife':
      // Actor tags Target as Wife -> Target is Wife.
      // Actor is Husband (if male or default) or Wife (if female).
      if (effectiveActorGender === 'FEMALE') {
        reciprocal = 'Wife';
      } else {
        reciprocal = 'Husband';
      }
      break;

    case 'Boyfriend':
      reciprocal = effectiveActorGender === 'MALE' ? 'Boyfriend' : 'Girlfriend';
      break;

    case 'Girlfriend':
      reciprocal = effectiveActorGender === 'FEMALE' ? 'Girlfriend' : 'Boyfriend';
      break;

    case 'Father':
    case 'Mother':
      // Target is Parent. Actor is Child (Daughter or Son).
      if (effectiveActorGender === 'FEMALE') {
        reciprocal = 'Daughter';
      } else if (effectiveActorGender === 'MALE') {
        reciprocal = 'Son';
      } else {
        isAmbiguous = true;
        reciprocal = 'Daughter'; // CycleCare core audience default
        determinedBy = 'DEFAULT';
      }
      break;

    case 'Daughter':
    case 'Son':
      // Target is Child. Actor is Parent (Mother or Father).
      if (effectiveActorGender === 'MALE') {
        reciprocal = 'Father';
      } else if (effectiveActorGender === 'FEMALE') {
        reciprocal = 'Mother';
      } else {
        isAmbiguous = true;
        reciprocal = 'Mother';
        determinedBy = 'DEFAULT';
      }
      break;

    case 'Brother':
    case 'Sister':
      // Target is Sibling. Actor is Sibling (Sister or Brother).
      if (effectiveActorGender === 'MALE') {
        reciprocal = 'Brother';
      } else if (effectiveActorGender === 'FEMALE') {
        reciprocal = 'Sister';
      } else {
        isAmbiguous = true;
        reciprocal = 'Sister';
        determinedBy = 'DEFAULT';
      }
      break;

    case 'Best Friend':
      reciprocal = 'Best Friend';
      break;

    case 'Partner':
      reciprocal = 'Partner';
      break;

    case 'Guardian':
      reciprocal = effectiveActorGender === 'MALE' ? 'Son' : 'Daughter';
      break;

    case 'Family':
      reciprocal = 'Family';
      break;

    case 'Other':
    default:
      reciprocal = 'Other';
      break;
  }

  const ambiguityOptions = getAmbiguityOptions(normAssigned);

  if (isAmbiguous && strictAmbiguity) {
    const err = new Error(`Reciprocal relationship for ${normAssigned} is ambiguous. Please select one of: ${ambiguityOptions.join(', ')}`);
    err.code = 'RECIPROCAL_RELATIONSHIP_AMBIGUOUS';
    err.statusCode = 422;
    err.options = ambiguityOptions;
    throw err;
  }

  return {
    assigned: normAssigned,
    reciprocal,
    isAmbiguous,
    ambiguityOptions: isAmbiguous ? ambiguityOptions : [],
    determinedBy
  };
}

module.exports = {
  CANONICAL_RELATIONSHIPS,
  COMPATIBILITY_RULES,
  normalizeRelationshipTag,
  validateCompatibility,
  getAmbiguityOptions,
  resolveEffectiveGender,
  determineReciprocal
};
