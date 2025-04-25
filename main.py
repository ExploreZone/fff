import time
import yaml
from src.data_fetcher import BinanceDataFetcher
from src.strategy_engine import StrategyEngine
from src.trade_executor import TradeExecutor
from src.logger import StrategyLogger


def load_config():
    """加载配置文件"""
    with open('config/api_config.yaml') as f:
        api_config = yaml.safe_load(f)
    with open('config/strategy_params.yaml') as f:
        strategy_config = yaml.safe_load(f)
    return {**api_config, **strategy_config}


def main():
    """主运行循环"""
    config = load_config()
    logger = StrategyLogger()

    # 初始化模块
    data_fetcher = BinanceDataFetcher(config)
    strategy = StrategyEngine(config, logger)
    executor = TradeExecutor(config, logger)

    print("=== 策略开始运行 ===")
    while True:
        try:
            # 获取数据
            df_5m, df_1h = data_fetcher.get_multitimeframe_data(config['symbol'])

            # 生成信号
            signal = strategy.generate_signal(df_5m, df_1h)

            if signal:
                # 获取当前价格
                current_price = df_5m['close'].iloc[-1]

                # 执行交易（模拟余额）
                executor.execute_order(signal,
                                       df_5m['atr'].iloc[-1],
                                       current_price,
                                       balance=1000)

            time.sleep(300)  # 5分钟间隔

        except KeyboardInterrupt:
            print("\n=== 策略手动终止 ===")
            break
        except Exception as e:
            logger.log_error(f"主循环错误: {str(e)}")
            time.sleep(60)


if __name__ == "__main__":
    main()