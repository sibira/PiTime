PiTime
====

RaspBerry Pi を卓上時計にします。

## 環境

OS:raspbian wheezy 7.8
モニタ:800×480

## Install

*time.cgi
/usr/lib/cgi-bin/に設置、実行権限変更
`sudo chown pi:pi time.cgi
`sudo chmod 755 time.cgi


*jquery.knob-1.2.12.min.js
*jquery-2.1.4.min.js

/var/www/jsに設置、実行権限変更
sudo mkdir /var/www/js
sudo chown pi:pi /var/www/js
sudo chmod 755 /var/www/js

*raspbian アップデート
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade
再起動
sudo apt-get autoremove

*perlのモジュールインストール
sudo cpan    （yes/noを聞かれたら、とりあえずエンター)
install JSON
install Calendar::Japanese::Holiday
exit

*その他必要なパッケージインストール
sudo apt-get install apache2
sudo apt-get install unclutter
sudo apt-get install midori
sudo apt-get install ethtool

*apacheの起動ユーザ変更
sudo nano /etc/apache2/apache2.conf（178行目あたり）

User ${APACHE_RUN_USER}
↓
User pi

*フルスクリーン設定
 sudo nano /etc/xdg/lxsession/LXDE-pi/autostart で以下を追加
 @/usr/bin/midori -e Fullscreen -a http://localhost/cgi-bin/time.cgi
 @unclutter
 @xset s off
 @xset s noblank
 @xset -dpms

*起動時、xwindowでデフォルト起動設定
 raspi-config
 3 Enable Boot to Desktop/Scratch
 Desktop Log in as user ‘pi’ at the graphical desktop を選択

*再起動後、時計の画面になっている筈。

## ライセンス

MIT ライセンス
    http://ja.wikipedia.org/wiki/MIT_License

## 免責事項

本ソフトウェアは使用者の責任において利用してください。 このプログラムによって発生したいかなる障害・損害も、作成者は一切責任を負わないものとします。また、本プログラムは予告なく削除または変更する場合があります。
