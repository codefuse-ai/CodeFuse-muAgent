import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';
import 'highlight.js/styles/github.css';
import MarkdownIt from 'markdown-it';
import React from 'react';
import { CodeWrapper } from './style';

type TemplateIprops = {
  dataSource: string;
};

const TemplateCode = ({ dataSource }: TemplateIprops) => {
  const md: any = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true,
    breaks: true,
    xhtmlOut: true,
    highlight: (str: any, lang: any) => {
      if (lang && hljs.getLanguage(lang)) {
        try {
          // 移除了添加行号的部分，直接返回hljs高亮的结果
          const highlightedCode = hljs.highlight(lang, str).value;
          return `<pre class="hljs github"><code class="hljs ${lang}">${highlightedCode}</code></pre>`;
        } catch (error) {
          console.error(error);
        }
      }
      // 如果没有识别到语言，则按原样返回
      return `<pre><code>${md.utils.escapeHtml(str)}</code></pre>`;
    },
  });

  md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
    const token = tokens[idx];
    token.attrPush(['target', '_blank']);
    return self.renderToken(tokens, idx, options);
  };

  return (
    <CodeWrapper>
      <div
        className="code_less"
        dangerouslySetInnerHTML={{
          __html: md.render(dataSource),
        }}
        style={{ display: 'block', width: '100%' }}
      />
    </CodeWrapper>
  );
};

export default TemplateCode;
