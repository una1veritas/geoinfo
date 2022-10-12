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

pacman -S base-devel

は問題なく完了しました。

pacman -S mingw-w64-x86_64-toolchain

は、
mingw-w64-x86_64-gcc-ada-12.2.0-3-any.pkg.tar.zst.sig
mingw-w64-x86_64-libgccjit-12.2.0-3-any.pkg.tar.zst.sig
についてダウンロードでエラーがでた場合でも、ada と ccjit は使わないので
mingw-w64-x86_64-gcc 
等必要なものがインストールされるまでリトライします。
（何度やろうがインストールされたものはパッケージ管理されているので問題ない。）

コマンド
make
gcc
g++
等を引数なしで実行して、（コマンドが見つからない　エラーではなく）
コマンドのエラー（no input file 等）が返ってくることで、
インストールされたことを確認できます

この段階で、シェルで簡単な C プログラムをコンパイルできることや、
make ができることを確認できます。
emacs エディタ１（デカい）を使いたければ、
pacman -S mingw-w64-x86_64-emacs
でインストールできます。


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
これらはそれぞれ標準のディレクトリですが、標準でない場合はそれぞれをコンパイル時に
インクルードディレクトリ、ライブラリディレクトリにそれぞれ指定する必要があります。

この段階で、SDL2_test プロジェクトや SDL2_gfx_test プロジェクト、geograph プロジェクト
は手動でコンパイルできます。
例）
$ cd /C/Users/Sin\ Shimozono/Documents/Projects/geoinfo/SDL2_gfx_test/
$ g++ -std=c++2a -O0 -g3 -o SDL_gfx_test.exe ./src/SDL_gfx_test.cpp -lmingw32 -lSDL2main -lSDL2 -lSDL2_gfx

（成功。./SDL_gfx_test.exe で実行できる。）

このようにライブラリを使ったり、言語標準 C++20 を指定するためのコンパイラのオプションなど
すべてのオプションや引数を間違いなく書くのは面倒であり、分割コンパイルをするとさらに面倒なので、
Makefile を書いて make コマンドでコンパイルするのが普通です。


3. Eclipse のインストールとコンパイルオプション等の指定

Eclipse をダウンロードしインストールします。
（C/C++ Developer でダウンロード／インストールしていない場合は、
C/C++ 開発ができるようプラグインもインストールしておきます。詳細はぐぐれ）
2022/10/12 現在 バージョン 2022-09。

ワークスペースを設定し（GitHub の Clone したレポジトリディレクトリーをそのままワークスペースにできる）、
SDL2_gfx_test や geograph 等の既存のプロジェクト（特定のプログラム開発をするフォルダ）をインポートします。
方法は、ぐぐれ。

メニュー  Project -> Properties でダイアログを開き、
C/C++ Build のサブメニュー Tool Chain Editor、
サブメニュー Settings の GCC C++ Compiler の Dialect、
C/C++ General のサブメニュー Paths and Symbols の Libraries ペーン
の内容を、このディレクトリに放り込んだ .jpg 画像のように入力／選択します。
これらは Makefile で書くのと同じ内容です。
（パスはインクルード、ライブラリどちらにも必要ありませんでした。）

ソースコードは GitHub から最新のものをダウンロードしてください。
インクルードファイルは以下のように指定されています。
#include <SDL2/SDL.h>
#include <SDL2/SDL2_gfxPrimitives.h>

以上