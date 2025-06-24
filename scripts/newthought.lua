function RawInline(el)
  if el.format == "latex" then
    local content = el.text:match("\\newthought%s*{(.-)}")
    if content then
      return pandoc.Span(pandoc.Str(content), {class = "newthought"})
    end
  end
end

function RawBlock(el)
  if el.format == "latex" then
    local content = el.text:match("\\newthought%s*{(.-)}")
    if content then
      return pandoc.Para({ pandoc.Span(pandoc.Str(content), {class = "newthought"}) })
    end
  end
end
