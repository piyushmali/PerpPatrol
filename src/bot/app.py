import argparse, asyncio
from .main import bootstrap
from .data.marketdata import MarketDataService
from .engine.quote_engine import QuoteEngine
from .engine.ti_optimizer import TIOPT
from .execution.executor import Executor
from .execution.woofi_client import WOOFiClient
from .risk.limits import RiskManager
from .risk.kill_switch import KillSwitches
from .compliance.checks import Compliance
from .telemetry.metrics import Metrics

async def run(config_path: str, overrides_path: str|None):
    cfg, log = bootstrap(config_path, overrides_path)
    md = MarketDataService(cfg, log)
    client = WOOFiClient(cfg, log)  # TODO implement API details
    executor = Executor(cfg, log, client)
    risk = RiskManager(cfg, log)
    ks = KillSwitches(cfg, log)
    comp = Compliance(cfg, log, client)
    qe = QuoteEngine(cfg, log)
    metrics = Metrics(cfg, log)
    tuner = TIOPT(cfg, log, metrics)

    await md.start()
    await client.connect()
    symbols = cfg["strategy"]["symbols"]
    for s in symbols: await md.subscribe_orderbook(s)

    log.info("Starting event loop")
    try:
        while True:
            for sym in symbols:
                ob = md.get_orderbook(sym)
                if not ob or not ob.ready(): continue
                quotes = qe.compute_quotes(sym, ob, inventory=executor.position_notional(sym))
                quotes = tuner.nudge(sym, ob, quotes, executor)
                if risk.pretrade_ok(sym, quotes) and comp.pretrade_ok(sym, quotes):
                    await executor.sync_quotes(sym, quotes)
                metrics.observe(sym, ob, executor)
            if ks.tripped(executor): 
                await executor.flatten_all()
                break
            await asyncio.sleep(0.2)
    finally:
        await client.close()
        await md.stop()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--overrides")
    args = ap.parse_args()
    asyncio.run(run(args.config, args.overrides))
