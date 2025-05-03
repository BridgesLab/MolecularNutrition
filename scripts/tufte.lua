local os = require("os")
local format = string.format

-- This function handles margin notes in Tufte style
local function MarginNote(el)
  return pandoc.Div(el.content, {class='margin-note'})
end

-- This function handles margin figures in Tufte style
local function MarginFigure(el)
  return pandoc.Div(el.content, {class='margin-figure'})
end

-- Main function for document transformation
function Pandoc(doc)
  -- Get last-update from metadata or fallback to today's date
  local last_update
  if doc.meta['last-update'] then
    last_update = pandoc.utils.stringify(doc.meta['last-update'])
  else
    last_update = os.date("%Y-%m-%d")
  end

  -- Create footer with author and update date
  local footer = pandoc.Div({
    pandoc.Para({pandoc.Str('Last updated: ' .. last_update)}),
    pandoc.Para({pandoc.Str('Author: Dave Bridges')}),
  }, {class='footer'})

  -- Add footer to document
  table.insert(doc.blocks, footer)

  -- Process margin notes and figures
  for i, block in ipairs(doc.blocks) do
    if block.t == 'Div' then
      if block.classes:includes('margin-note') then
        doc.blocks[i] = MarginNote(block)
      elseif block.classes:includes('margin-figure') then
        doc.blocks[i] = MarginFigure(block)
      end
    end
  end

  return doc
end
