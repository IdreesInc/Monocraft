#!/bin/bash
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
	mv "$file" "Monocraft-ttf/weights/$file"
done

mkdir -p Monocraft-otf/weights
for file in Monocraft-*.otf; do
	mv "$file" "Monocraft-otf/weights/$file"
done

zip -r Monocraft-ttf.zip Monocraft-ttf
zip -r Monocraft-otf.zip Monocraft-otf

if [ $# -ne 0 ] && [ $1 = "nerd" ]
then
	echo "Building Nerd Fonts"
	cd ../build
	# python3.12 ./nerd-fonts/font-patcher ../dist/Monocraft.ttf --complete --careful --outputdir ../dist/
	python3.12 ./nerd-fonts/font-patcher ../dist/Monocraft.ttc --complete --careful --outputdir ../dist/
	cd ../dist
	# mv "Monocraft Nerd Font Complete.ttf" "Monocraft-nerd-fonts-patched.ttf"
	mv "Monocraft Nerd Font.ttc" "Monocraft-nerd-fonts-patched.ttc"
fi