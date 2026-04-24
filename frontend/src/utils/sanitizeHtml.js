import DOMPurify from 'dompurify'

const SANITIZE_OPTIONS = {
  ALLOWED_TAGS: [
    'a',
    'b',
    'blockquote',
    'br',
    'em',
    'h1',
    'h2',
    'h3',
    'h4',
    'li',
    'ol',
    'p',
    'strong',
    'u',
    'ul',
  ],
  ALLOWED_ATTR: ['href', 'rel', 'target'],
  ALLOW_DATA_ATTR: false,
  FORBID_ATTR: ['style'],
  FORBID_TAGS: ['form', 'iframe', 'input', 'meta', 'script', 'style'],
}

export function sanitizeRichHtml(html) {
  return DOMPurify.sanitize(html || '', SANITIZE_OPTIONS)
}