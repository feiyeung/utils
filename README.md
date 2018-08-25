# utils
scripts for my convenience 

example of obatining a list of sha1sum to JPEG and PNG files (by extension)
`find $PWD \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) -type f | xargs sha1sum`
