import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-dark.css';
import 'highlight.js/styles/github.css';
import MarkdownIt from 'markdown-it';
import React, { useState, useEffect } from 'react';
import { CodeWrapper } from './style';

type TemplateIprops = {
  dataSource: string;
};

const TemplateCode = ({ dataSource }: TemplateIprops) => {
  const [visibleText, setVisibleText] = useState('');

  const md: any = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true,
    breaks: true,
    xhtmlOut: true,
    highlight: (str: any, lang: any) => {
      if (lang && hljs.getLanguage(lang)) {
        try {
          const highlightedCode = hljs.highlight(lang, str).value;
          return `<pre class="hljs github"><code class="hljs ${lang}">${highlightedCode}</code></pre>`;
        } catch (error) {
          console.error(error);
        }
      }
      return `<pre><code>${md.utils.escapeHtml(str)}</code></pre>`;
    },
  });

  md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
    const token = tokens[idx];
    token.attrPush(['target', '_blank']);
    return self.renderToken(tokens, idx, options);
  };

  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      setVisibleText((prevText) => {
        if (index < dataSource.length) {
          index++;
          return dataSource.slice(0, index);
        } else {
          clearInterval(interval);
          return dataSource;
        }
      });
    }, 20); // 调整这个值以改变打字速度

    return () => {
      clearInterval(interval);
    };
  }, [dataSource]);

  return (
    <CodeWrapper>
      <div
        className="code_less"
        dangerouslySetInnerHTML={{
          __html: md.render(visibleText),
        }}
        style={{ display: 'block', width: '100%' }}
      />
    </CodeWrapper>
  );
};

export default TemplateCode;
