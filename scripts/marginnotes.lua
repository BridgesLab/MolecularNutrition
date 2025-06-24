function RawBlock(el)
  if el.format == "latex" then
    el.text = el.text
      :gsub("\\marginnote%s*{(.-)}", "^[%1]")
      :gsub("\\sidenote%s*{(.-)}", "^[%1]")
    return pandoc.RawBlock("markdown", el.text)
  end
end

function RawInline(el)
  if el.format == "latex" then
    local newtext = el.text
      :gsub("\\marginnote%s*{(.-)}", "^[%1]")
      :gsub("\\sidenote%s*{(.-)}", "^[%1]")
    return pandoc.RawInline("markdown", newtext)
  end
end
