lua << EOF
local map = vim.api.nvim_set_keymap

-- write all buffers, format python files and reload all buffers
map('n', '<f1>', ':wa<cr>:!source venv/bin/activate && black watson_jira/<cr>:windo e<cr>', { noremap = true, silent = true })


EOF
