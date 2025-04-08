<template>
  <div v-html="renderedContent" ref="mathContainer"></div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { renderMarkdown } from '@/assets/js/markdown.js';
import katex from 'katex';

const content = ref('')
const renderedContent = ref('')

content.value = `泰勒公式是数学分析中的一个重要工具，它提供了一种方法来用多项式逼近一个函数。这种逼近在很多情况下都非常有用，尤其是在计算和理论分析中。下面我将简要介绍几个常见的泰勒公式。 ###1. 泰勒公式的定义 对于一个在点 \\(a\\) 处具有所有阶导数的函数 \\(f(x)\\)，其在 \\(a\\) 点的泰勒级数可以表示为： \\[ f(x) = f(a) + \\frac{f'(a)}{1!}(x-a) + \\frac{f''(a)}{2!}(x-a)^2 + \\cdots + \\frac{f^{(n)}(a)}{n!}(x-a)^n + R_n(x) \\] 其中，\\(R_n(x)\\) 是余项，表示泰勒多项式与实际函数之间的差异。`;
renderedContent.value = renderMarkdown(content.value)
const latex_content = "这个 ## 标题 就是寻"
console.log(renderMarkdown(latex_content));

onMounted(() => {
  // 确保 Vue 渲染完成后再进行 KaTeX 渲染
  nextTick(() => {
    const mathContainer = document.querySelector('[ref="mathContainer"]');
    if (mathContainer) {
      katex.render(mathContainer.innerHTML, mathContainer);
    }
  });
});
</script>

<style scoped>
@import 'katex/dist/katex.min.css';

</style>
