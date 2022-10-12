SDL2 を使うプログラムの開発を MinGW64 ではじめるための手順


ここでは、（すでに Msys がインストールされている場合は
アンインストールして）C: に Msys2 ディレクトリもない状態ではじめます。

1. MSYS2 (M) と MinGW64 ツールチェーンのインストール

Google で「Msys2 MinGW インストール」を検索すると、日本語のサイトでは
以下がトップに出ます（2022/10/12）。この内容のとおりに、まず MSys2 を
インストールします。
ダウンロードできるインストーラは 2022/10/12 現在 msys2-x86_64-20220904.exe です。

MSYS2/MinGW-w64 (64bit/32bit) インストール手順 メモ
https://gist.github.com/Hamayama/eb4b4824ada3ac71beee0c9bb5fa546d

このページの手順 3 までを行い、
最新版へのアップデートと 64 bit 開発ツールチェーンのインストールをすませます。

mingw-w64-x86_64-gcc-ada-12.2.0-3-any.pkg.tar.zst.sig
mingw-w64-x86_64-libgccjit-12.2.0-3-any.pkg.tar.zst.sig
についてダウンロードでエラーがでましたが、ada と ccjit は使わないので
無視することにします。


2. SDL2 と SDL2_gfx のインストール

ここでは Msys2/Mingw64 に用意されているバイナリーパッケージでインストールします。
メニューから MSYS2 MINGW64 シェルを開き、以下を実行します。

pacman -S mingw-w64-x86_64-SDL2
pacman -S mingw-w64-x86_64-SDL2_gfx

※ SDL2 ではない SDL（SDL のバージョン 1）を間違ってインストールしないこと。

すると、インクルードファイルが /mingw64/include/SDL2 ディレクトリに、
ライブラリファイルが /mingw64/lib
にインストールされます。

ls /mingw64/include/SDL2/
ls /mingw64/lib/libSDL2*

等で確認できます。

