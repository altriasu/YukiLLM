import MarkdownIt from 'markdown-it';
import markdownItKatex from '@iktakahiro/markdown-it-katex';
import DOMPurify from 'dompurify';

// 初始化 MarkdownIt，支持 LaTeX、换行、链接
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true,
})
  .use(markdownItKatex, {
    strict: false
  });

/**
 * 渲染 Markdown 内容，支持 typewriter 流式逐字渲染。
 * @param {string} rawText 原始字符串
 * @returns {string} 渲染后的 HTML
 */
export function renderMarkdown(rawText) {
  try {
    const replacedText = rawText
      .replace(/([^\n])(\n?)(#{1,5})/g, '\n$1\n$3 ')      
      .replace(/\\\[/g, '\n$$$')
      .replace(/\\\]/g, '$$$\n')
      .replace(/\\\(/g, '$')
      .replace(/\\\)/g, '$')

    // 2. 渲染 Markdown 内容
    let renderedHTML = md.render(replacedText);

    // 3. 使用 DOMPurify 清理潜在的恶意代码
    const finalHTML = DOMPurify.sanitize(renderedHTML);

    // return replacedText;
    return finalHTML;
  } catch (e) {
    console.error('Markdown 渲染出错:', e);
    return rawText; // fallback
  }
}
