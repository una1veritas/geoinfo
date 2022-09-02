SDL2 ベースのグラフィクスプログラムを Msys64/Mingw64 で動かすためのメモ

1. SDL2 ライブラリのパッケージを pacman でインストールする。
SDL2 は楕円など一部グラフィクスプリミティブの描画関数がないので
SDL2 gfx ライブラリで補う。

pacman -S mingw-w64-x86_64-SDL2
pacman -S mingw-w64-x86_64-SDL2_gfx

2. コンパイラのインクルードパス、リンクライブラリーパス、ライブラリ名を設定する。
Eclipse では C/C++ General -> Paths and Symbols
注意) WinMain undefined エラーになるので、ライブラリ mingw32 の追加が必要。
Includes:
/msys64/mingw64/include/SDL2
Library paths:
/msys64/mingw64/lib
Libraries:
SDL2main
SDL2
SDL2_gfx
mingw32

注意） g++ のバグ？ ライブラリのリンクの順番は SDL2main を SDL2 より先に持ってくると、
リンカエラー undefined reference to `SDL_strlen' 等がなくなる。

3. GFX のグラフィクスプリミティブ関数 xxxColor の 4 バイト整数での色指定が、
エンディアンネスのためかバイトオーダーが逆になっているので注意する。
0xAABBGGRR になる。AA はアルファ値（透明度）