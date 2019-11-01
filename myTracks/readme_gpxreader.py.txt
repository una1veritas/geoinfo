gpxreader.py バージョン -0.9
（変更点）

時刻を修正ユリウス日で出力するオプション -mjd を追加．

--------------------------
gpxreader.py バージョン -1.0
（変更点）

3. コマンドプログラムとして使用する。
コマンドシェル（Mac OS ならターミナル）で python3、gpxreader.py と .gpx ファイルのディレクトリ
を確認する。python3 のコマンドディレクトリはシェルのコマンドパスにはいっており
gpxreader.py と .gpx ファイルは両方ともカレントワーキングディレクトリにあるとすると、

python3 gpxreader.py gpxファイル名 （CSVファイル名） [return]

でプログラムが起動し、内容の位置点列をコンソールに出力表示し、同時に CSV ファイルに
書き込む。
CSV ファイル名を省略すると、.gpx ファイルに含まれるトラック trk の名前を使ってファイル名を自動生成する．

引数にオプション -elev をくわえると，高度 elevation のカラムを追加し出力する．
引数にオプション -mytracks をくわえると，myTracks の gpx 拡張による speed のカラムを追加し出力する．

--------------------------
gpxreader.py バージョン -2.0

（変更点）
3. コマンドプログラムとして使用する。
コマンドシェル（Mac OS ならターミナル）で python3、gpxreader.py と .gpx ファイルのディレクトリ
を確認する。python3 のコマンドディレクトリはシェルのコマンドパスにはいっており
gpxreader.py と .gpx ファイルは両方ともカレントワーキングディレクトリにあるとすると、

python3 gpxreader.py gpxファイル名 （CSVファイル名） [return]

でプログラムが起動し、内容の位置点列をコンソールに出力表示し、同時に CSV ファイルに
書き込む。
CSV ファイル名を省略すると、.gpx ファイルに含まれるトラック trk の名前を使ってファイル名を自動生成する．

--------------------------
gpxreader.py バージョン -3.0

.gpx ファイル（XML）から位置点の列を読み出し CSV ファイル（テキスト、コンマ区切り）に
変換するプログラム gpxreader.py の使い方：

1. Python3 がインストールされていることを確認する。
使用OSに未インストールなら、サイト python.org でOSに対応したバイナリをダウンロードし
インストールしておく。

2. gpxreader.py をダウンロードする。
https://github.com/una1veritas/GoogleAPI/tree/master/myTracks/gpxReader
にあるので（レポジトリ全体か個別にファイルを）ダウンロードする。

3. コマンドプログラムとして使用する。
コマンドシェル（Mac OS ならターミナル）で python3、gpxreader.py と .gpx ファイルのディレクトリ
を確認する。python3 のコマンドディレクトリはシェルのコマンドパスにはいっており
（python3 [return] でインタプリタが実行できる。インタプリタの終了は quit() [return]）
gpxreader.py と .gpx ファイルは両方ともカレントワーキングディレクトリにあるとすると、

python3 gpxreader.py gpxファイル名 CSVファイル名 [return]

でプログラムが起動し、内容の位置点列をコンソールに出力表示し、同時に CSV ファイルに
書き込む。

おわり

