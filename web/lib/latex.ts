/**
 * Utility functions for LaTeX processing
 *
 * remark-math only supports $...$ and $$...$$ delimiters by default.
 * Many LLMs output LaTeX using \(...\) and \[...\] delimiters.
 * This utility converts between formats.
 */

/**
 * Convert LaTeX delimiters from \(...\) and \[...\] to $...$ and $$...$$
 * This makes the content compatible with remark-math for ReactMarkdown rendering.
 *
 * @param content - The content containing LaTeX with \(...\) or \[...\] delimiters
 * @returns Content with $...$ and $$...$$ delimiters
 */
export function convertLatexDelimiters(content: string): string {
  if (!content) return content;

  let result = content;

  // Convert \[...\] to $$...$$ (block math)
  // Use a regex that handles multiline content
  // Note: In JSON strings, \[ becomes \\[ which in JS becomes \[
  result = result.replace(/\\\[([\s\S]*?)\\\]/g, "\n$$\n$1\n$$\n");

  // Convert \(...\) to $...$ (inline math)
  // Be careful not to match escaped parentheses in other contexts
  result = result.replace(/\\\(([\s\S]*?)\\\)/g, " $$$1$$ ");

  // Wrap bare \frac{a}{b} and \dfrac{a}{b} that are NOT already inside $...$ delimiters.
  // This handles options/answers stored without \(...\) wrappers, e.g. \frac{5}{8}.
  // Strategy: count $ signs before the match position — if odd, we're inside math mode already.
  result = result.replace(/\\(?:d)?frac\{[^}]+\}\{[^}]+\}/g, (match, offset, str) => {
    const dollarCount = (str.slice(0, offset).match(/\$/g) || []).length;
    if (dollarCount % 2 === 1) return match; // already inside $...$ math environment
    return `$${match}$`;
  });

  // Clean up multiple consecutive newlines
  result = result.replace(/\n{3,}/g, "\n\n");

  return result;
}

/**
 * Process content for ReactMarkdown rendering with proper LaTeX support
 * This is a convenience wrapper that applies all necessary transformations.
 *
 * @param content - The raw content to process
 * @returns Processed content ready for ReactMarkdown with remark-math
 */
export function processLatexContent(content: string): string {
  if (!content) return "";

  // Convert to string if not already
  const str = String(content);

  // Apply delimiter conversion
  return convertLatexDelimiters(str);
}
