import MarkdownIt from 'markdown-it';
import markdownItKatex from '@iktakahiro/markdown-it-katex';
import DOMPurify from 'dompurify';
import hljs from 'highlight.js';
import 'highlight.js/styles/default.css'; 

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

hljs.configure({
  useBR: true,
  ignoreUnescapedHTML: true,
})

function renderCodeBlocks() {
  document.querySelectorAll('pre code').forEach((codeBlock) => {
    if (!codeBlock.dataset.highlighted) {
      hljs.highlightElement(codeBlock);
      codeBlock.dataset.highlighted = 'true'; // 设置已高亮标记
    }
    const preBlock = codeBlock.closest('pre');
    if (!preBlock.dataset.codeHeadAdded && !preBlock.querySelector('.code-head')) {
      const codeBody = preBlock.querySelector('code');
      const codeType = codeBlock.classList[0]?.replace('language-', '') || 'code';
      const htmlToInsert = `<div class="code-head"><span class="code-head-title">${codeType}</span> <span class="code-copy-btn" title="复制代码"><svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg></span></div>`;
      preBlock.insertAdjacentHTML('afterbegin', htmlToInsert);
      preBlock.dataset.codeHeadAdded = 'true';
    }
  });
  document.querySelectorAll('.code-copy-btn').forEach((copyBtn) => {
    if (!copyBtn.dataset.bindCopy) {
      copyBtn.addEventListener('click', () => {
        const preBlock = copyBtn.closest('pre');
        const codeBlock = preBlock?.querySelector('code');
        if (codeBlock) {
          const text = codeBlock.innerText;
          navigator.clipboard.writeText(text).then(() => {
            copyBtn.title = '已复制';
            copyBtn.classList.add('copied');
            setTimeout(() => {
              copyBtn.title = '复制代码';
              copyBtn.classList.remove('copied');
            }, 1500);
          }).catch(err => {
            console.error('复制失败:', err);
          });
        }
      });
      copyBtn.dataset.bindCopy = 'true'; // 防止重复绑定
    }
  });
}


/**
 * 渲染 Markdown 内容，支持 typewriter 流式逐字渲染。
 * @param {string} rawText 原始字符串
 * @returns {string} 渲染后的 HTML
 */
let renderTimer = null;
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

    setTimeout(() => {
      renderCodeBlocks();
      // hljs.highlightAll();
    }, 1000);
    
    // if (renderTimer) clearTimeout(renderTimer);
    // renderTimer = setTimeout(() => {
    //   addHtmlToCodeBlocks();
    // }, 100);

    return finalHTML;
  } catch (e) {
    console.error('Markdown 渲染出错:', e);
    return rawText; // fallback
  }
}
