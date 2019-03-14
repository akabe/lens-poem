# レンズポエムの自動生成

レンズ交換式カメラ向けのレンズのキャッチコピー（通称：レンズポエム）を自動生成します。

## 学習データのスクレイピング

スクレイピングの後、学習しやすいように手動で前処理しています。

```
python canon.py
python nikon.py
python sigma.py
python tamron.py
python sony.py
python fujifilm.py
```

## マルコフ連鎖

```
python markov_chain.py --context 2 *.csv
```
