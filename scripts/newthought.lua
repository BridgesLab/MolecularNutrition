-- scripts/newthought.lua

function RawInline(el)
  if el.format == "latex" and el.text:match("\\newthought{") then
    local content = el.text:match("\\newthought{(.*)}")
    return pandoc.RawInline("html", '<span class="newthought">' .. content .. '</span>')
  end
end
