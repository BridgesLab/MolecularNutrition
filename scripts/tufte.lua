-- tufte.lua
local format = string.format

-- This function handles margin notes in Tufte style
function MarginNote(el)
  -- We assume that the margin note is a div with class 'margin-note'
  return pandoc.Div(el.content, {class='margin-note'})
end

-- This function handles margin figures in Tufte style
function MarginFigure(el)
  -- We assume that the margin figure is a div with class 'margin-figure'
  return pandoc.Div(el.content, {class='margin-figure'})
end

-- This function ensures that the footer (for the page number) is added in the correct format
function Header(doc)
  -- Get the date the file was last updated (use the metadata field `last-update` if it's available)
  local last_update = doc.meta['last-update'] or os.date("%Y-%m-%d")
  -- Modify the footer to include the last update
  local footer = pandoc.Div({
    pandoc.Para({pandoc.Str('Last updated: ' .. last_update)}),
    pandoc.Para({pandoc.Str('Author: Dave Bridges')}),
  }, {class='footer'})

  -- Add the footer to the document
  table.insert(doc.blocks, footer)
  
  return doc
end

-- This function modifies the headers and footers
function Pandoc(doc)
  -- Tufte-style requires specific page styling, so modify the document for Tufte style
  doc = Header(doc)

  -- Handle margin notes and figures
  for i, block in ipairs(doc.blocks) do
    if block.t == 'Div' then
      -- Check if it's a margin note or figure
      if block.classes:includes('margin-note') then
        doc.blocks[i] = MarginNote(block)
      elseif block.classes:includes('margin-figure') then
        doc.blocks[i] = MarginFigure(block)
      end
    end
  end

  return doc
end
