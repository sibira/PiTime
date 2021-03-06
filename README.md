PiTime
====

引き出しの奥で腐っているRaspBerry Piを卓上時計に調理します。

## 環境

OS:raspbian wheezy 7.8  
モニタ:800×480  
無線or有線による外部ネットワーク接続  
天気出力は日本の地域のみ対応  

## 動作画面
[Blog(外部)](http://www.netf.co.jp/blog/tech/raspberry-pi-%E3%81%A7%E5%8D%93%E4%B8%8A%E6%99%82%E8%A8%88%E3%82%92%E4%BD%9C%E3%81%A3%E3%81%A6%E3%81%BF%E3%81%BE%E3%81%97%E3%81%9F/)

![pic](./sample.jpg)

## 外部ライブラリ  
[jquery](https://github.com/jquery/jquery) (jquery-2.1.4.min.js)  
[jquery.knob](https://github.com/aterrien/jQuery-Knob) (jquery.knob-1.2.12.js)   

## インストール方法

--------------------------------------

* time.cgi  
  /usr/lib/cgi-bin/に設置、実行権限変更してください  
  sudo chown pi:pi time.cgi  
  sudo chmod 755 time.cgi  

--------------------------------------

* jquery.knob-1.2.12.min.js  
* jquery-2.1.4.min.js  
  以下ディレクトリを作り、/var/www/jsに設置してください  
  sudo mkdir /var/www/js  
  sudo chown pi:pi /var/www/js  
  sudo chmod 755 /var/www/js  

--------------------------------------

* perlのモジュールインストール  
  sudo cpan    （yes/noを聞かれたら、とりあえずエンター)  
  install JSON  
  install Calendar::Japanese::Holiday  
  exit  

--------------------------------------

* 必要なパッケージインストール  
  sudo apt-get update  
  sudo apt-get install apache2  
  sudo apt-get install unclutter  
  sudo apt-get install midori  
  sudo apt-get install ethtool  

--------------------------------------

* apacheの起動ユーザ変更  
  sudo nano /etc/apache2/apache2.conf（178行目あたり）  
  User ${APACHE_RUN_USER}  
  ↓  
  User pi  

--------------------------------------

* フルスクリーン設定  
  sudo nano /etc/xdg/lxsession/LXDE-pi/autostart で以下を追加  
  @/usr/bin/midori -e Fullscreen -a http://localhost/cgi-bin/time.cgi  
  @unclutter  
  @xset s off  
  @xset s noblank  
  @xset -dpms  

--------------------------------------

* 起動時、xwindowでデフォルト起動設定  
  raspi-config  
  3 Enable Boot to Desktop/Scratch  
  Desktop Log in as user ‘pi’ at the graphical desktop を選択  

--------------------------------------

* 再起動後、時計の画面になっている筈。  

--------------------------------------

## パラメータ変更  

* ネットワークインターフェース(wlan* or eth*)  
my $para_wlan0 = “wlan0”;  

* 再生デイバス番号(番号 or none)  
my $para_int_vol1 = “0”;  
* 録音デイバス番号(番号 or none)  
my $para_int_vol2 = “1”;  
ここの番号は、amixer -c ● の黒丸の番号になります。  

* お天気の地域設定  
my $weather_area = “130010”;  

地域の番号を入力しないといけません（設定されているのは東京です）  
http://weather.livedoor.com/weather_hacks/webservice  

番号わからないという方は  
http://weather.livedoor.com/  
から各地の天気のページにいったURLのアドレスが各都道府県になっている様子  

例）長野だと以下のURLになるのでパラメーターは200010  
http://weather.livedoor.com/area/forecast/200010  

設定が終わったら、キーボードのF5を押して画面をリロードしてみてください。  

エラーメッセージがデフォルトで出るようであれば、ソース内の以下欄をいじってみてください  
* #dmesg内でエラーと判断するもの  
* #エラーと判断した行で以下文字が入っていた場合除外  

## ライセンス

This software is released under the [MIT Licenses](https://opensource.org/licenses/mit-license.php)

## 免責事項

本ソフトウェアは使用者の責任において利用してください。  
このプログラムによって発生したいかなる障害・損害も、作成者は一切責任を負わないものとします。  
また、本プログラムは予告なく削除または変更する場合があります。  
