function RawInline(el)
  if el.format == "latex" then
    print("RawInline: " .. el.text)
    local content = el.text:match("\\newthought%s*{(.-)}")
    if content then
      print("Matched newthought: " .. content)
      return pandoc.Span(pandoc.Str(content), {class = "newthought"})
    end
  end
end

function RawBlock(el)
  if el.format == "latex" then
    print("RawBlock: " .. el.text)
    local content = el.text:match("\\newthought%s*{(.-)}")
    if content then
      print("Matched BLOCK newthought: " .. content)
      return pandoc.Para({ pandoc.Span(pandoc.Str(content), {class = "newthought"}) })
    end
  end
end
