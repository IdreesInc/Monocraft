#!/bin/bash

echo "Beginning to craft Monocraft..."
cd ../src

rm -rf ../dist
mkdir -p ../dist

python3.12 ../src/monocraft.py -a --output-ttc

cd ../dist
mkdir -p Monocraft-otf
mkdir -p Monocraft-ttf
mkdir -p Monocraft-otf/weights
mkdir -p Monocraft-ttf/weights

mv Monocraft.ttf Monocraft-ttf/Monocraft.ttf
mv Monocraft.otf Monocraft-otf/Monocraft.otf

mkdir -p Monocraft-ttf/weights
for file in Monocraft-*.ttf; do
	ttfautohint --fallback-stem-width=60  --stem-width-mode="nnn" --no-info "$file" "hinted-$file"
	mv "hinted-$file" "$file"
	mv "$file" "Monocraft-ttf/weights/$file"
done

mkdir -p Monocraft-otf/weights
for file in Monocraft-*.otf; do
	mv "$file" "Monocraft-otf/weights/$file"
done

zip -r Monocraft-ttf.zip Monocraft-ttf
zip -r Monocraft-otf.zip Monocraft-otf

ttfautohint --fallback-stem-width=60  --stem-width-mode="nnn" --no-info "Monocraft.ttc" "hinted-Monocraft.ttc"
mv "hinted-Monocraft.ttc" "Monocraft.ttc"

if [ $# -ne 0 ] && [ $1 = "nerd" ]
then
	echo "Building Nerd Fonts"
	cd ../build
	fontforge --script FontPatcher/font-patcher --complete --careful --mono --makegroups -1 '../dist/Monocraft.ttc'
	mv 'Monocraft.ttc' '../dist/Monocraft-nerd-fonts-patched.ttc'
	cd ../dist
fi

echo "Crafting complete!"