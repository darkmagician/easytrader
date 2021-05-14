# easytrader



common trader for ths.



## Prerequisite
### Client
* 东北证券独立委托系统 (http://www.nesc.cn/dbzq/wsyyt/jcyw/rjxz.jsp)

* 国元同花顺独立交易版 (https://www.gyzq.com.cn/main/wangting/software_download/index.html)

在开始之前，请对客户端调整以下设置，不然会导致下单时价格出错以及客户端超时锁定。

    系统设置 > 界面设置: 界面不操作超时时间设为 0
    系统设置 > 交易设置: 默认买入价格/买入数量/卖出价格/卖出数量 都设置为 空

### Python dependency

* install anaconda 
* run the following command
```shell
pip install -r requirements.txt
```

## Validated Features
* balance
* positions
* buy
* sell
*