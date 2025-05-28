# 法政大学生向け新SNS

## 背景

「法政生の法政生による法政生のＳＮＳ」というテーマのもと、法政大学の学生対象としてSNSを製作する。学生同士にコミュニケーションを円滑に、学生生活を豊かにするという方針の下、大学生にとって役立つ機能を採用する。

## プロジェクト

このプロジェクトについて基本的に連絡はDiscordで行う。バージョン管理にはGitHubを用いるためプロジェクトに参画するメンバーは全員GitHubを最低限理解していることが望ましい。参加メンバーはLINE投票「サークルでの政策で参加したいものを選んでください！」に投票した人とする（現在（2025年5月15日）17名）。

## サイト構成

以前より「たまっぷ」で使用しているロリポップサーバでFlaskを用いて実現する。開発に使用するPCはPythonが動くものであればOSは問わない。
サイトマップは以下のとおりである。
- サインアップ画面
- ログイン画面
- ホームタブ
  - 学生の間で人気の話題
  - 話題の検索結果
- フレンドタブ
  - フレンド
  - キュリアス
- 時間割タブ
  - 時間割に対応するフレンド一覧
- アバウトミータブ
  - 自分の投稿
  - 好きな投稿
  - DM

## システム要件
ページレイアウトは草案にしたがっていく。ただし実現が困難なものに関してはUXを損なわない範囲でデザインを変更する。時間割機能については一定間隔で法政大学シラバスからスクレイピングしデータベースを最新の状態に保つ必要がある。また、DM機能はユーザ同士のメッセージ入力がリアルタイムで確認できる仕組みにする。

### 技術要件
開発に用いる言語は主にPython、HTML、CSSである。ただし、CSSについてはCSSフレームワークの一種であるTailwind CSSを使用する。素のCSSではページの構造が複雑になるにつれクラスの命名が複雑になるという問題を回避するためである。
## 素のCSSの場合
```
<div class="container">
  <div class="row">
    <div class="col-12">
      <h1>タイトル</h1>
    </div>
  </div>
</div>
```
### Tailwind CSSの場合
```
<div class="max-w-3xl mx-auto">
  <div class="flex flex-col gap-4">
    <div class="flex flex-col gap-2">
      <h1>タイトル</h1>
    </div>
  </div>
</div>
```

前述のとおりロリポップサーバを利用する。Flaskのデプロイはノウハウが確立している。データベースは開発段階ではSQLite、本番環境ではMySQLを用いる。これらのデータベースの移行はORMを用いることに速やかに行うことができる。データベースの操作にはFlask用のORMライブラリであるflask-sqlalchemyを用いる。データベースの操作はORMを介して行い、生のSQLは使用しない。

## データベース

データベースは開発段階ではSQLite、本番環境ではMySQLを用いる。これらのデータベースの移行はORMを用いることに速やかに行うことができる。データベースの操作にはFlask用のORMライブラリであるflask-sqlalchemyを用いる。データベースの操作はORMを介して行い、生のSQLは使用しない。

### テーブル

テーブルは以下のとおりである。

|テーブル名|説明|
|---|---|
|users|ユーザー情報|
|posts|投稿情報|
|reactions|投稿へのリアクション情報|
|friends|フレンド情報|
|classes|授業情報|
|class_entries|授業の登録情報|

#### usersテーブル

|カラム名|型|説明|
|---|---|---|
|id|UUID|ユーザーID|
|username|String|ユーザー名|
|email|String|メールアドレス|
|password|String|パスワード|
|created_at|DateTime|作成日時|
|department|String|学部|

#### postsテーブル

|カラム名|型|説明|
|---|---|---|
|id|UUID|投稿ID|
|title|String|タイトル|
|content|String|内容|
|ip|String|IPアドレス|
|created_at|DateTime|作成日時|
|user_id|UUID|ユーザーID|

#### reactionsテーブル

|カラム名|型|説明|
|---|---|---|
|id|UUID|リアクションID|
|post_id|UUID|投稿ID|
|user_id|UUID|ユーザーID|
|reaction|String|リアクション|
|created_at|DateTime|作成日時|

#### friendsテーブル

|カラム名|型|説明|
|---|---|---|
|id|UUID|フレンドID|
|user_id|UUID|ユーザーID|
|friend_id|UUID|フレンドID|
|created_at|DateTime|作成日時|

#### classesテーブル

|カラム名|型|説明|
|---|---|---|
|id|UUID|授業ID|
|department|String|学部|
|year|Integer|年|
|code|String|授業コード|
|name|String|科目名|
|season|String|開講時期|
|time|Integer|時限|
|day|String|曜日|
|place|String|教室|
|unit|Integer|単位数|
|url|String|シラバスURL|
|teacher|String|講師|
|grade_min|Integer|配当年次_最小|
|grade_max|Integer|配当年次_最大|
|note|String|備考|
|error|String|エラー|
|is_spring|Boolean|春学期かどうか|
|is_autumn|Boolean|秋学期かどうか|

#### class_entriesテーブル

|カラム名|型|説明|
|---|---|---|
|id|UUID|授業登録ID|
|class_id|UUID|授業ID|
|user_id|UUID|ユーザーID|
|created_at|DateTime|作成日時|

### テーブルの関係

テーブルの関係は以下のとおりである。

```
users
  - posts
  - reactions
  - friends
  - classes
  - class_entries
```
```
posts
  - reactions
```
```
reactions
  - posts
```
```
friends
  - users
```
```
classes
  - class_entries
```
```
class_entries
  - classes
```

