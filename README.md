这是我个人博客除了资源和配置文件外的源码，生成器是 `hexo`，另外采用我自建的 `htmlstyle` 主题。

虽然大部分代码并不能拿来就用，但是静态网站的生成思路是相通的。如果有能帮到你的地方，请自取。

这套源码本身也受益于众多开源项目。

# 项目组织

```
scaffolds/              - 模板目录
themes/                 - 主题目录
    ...
        layout/         - 页面布局和逻辑
        source/         - 页面样式等
_config.yml
_config.htmlStyle.yml   - 配置文件
package.json
package-lock.json       - 依赖等
```

有部分涉及个人信息的内容我作了处理，当然你可以简单地绕过，但请注意，资源路径下的原创文字及图片内容采用 [CC-BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh) 授权协议。
