import argparse, yaml, time
from .exchange_sim import SimExchange
from ..bot.data.marketdata import MarketDataService
from ..bot.engine.quote_engine import QuoteEngine
from ..bot.execution.executor import Executor
from ..bot.execution.woofi_client import WOOFiClient
from ..bot.risk.limits import RiskManager
from ..bot.compliance.checks import Compliance

def main(config_path, overrides_path=None):
    with open(config_path,"r") as f: cfg = yaml.safe_load(f)
    if overrides_path:
        with open(overrides_path,"r") as f: cfg |= yaml.safe_load(f)
    sim = SimExchange()
    md = MarketDataService(cfg, None)
    qe = QuoteEngine(cfg, None)
    client = WOOFiClient(cfg, None)
    ex = Executor(cfg, None, client)
    risk = RiskManager(cfg, None)
    comp = Compliance(cfg, None, client)

    symbol = cfg["strategy"]["symbols"][0]
    md._books[symbol] = sim.step()
    pnl = 0.0
    for t in range(3000):
        ob = sim.step()
        md._books[symbol] = ob
        q = qe.compute_quotes(symbol, ob, ex.position_notional(symbol))
        if risk.pretrade_ok(symbol, q) and comp.pretrade_ok(symbol, q):
            # pretend fills occur if mid crosses
            ex._orders.setdefault(symbol,{})['bid']="bid"
            ex._orders.setdefault(symbol,{})['ask']="ask"
        if t%500==0:
            print(f"t={t} mid={ob.mid():.2f} spread={ob.spread():.4f}")
        time.sleep(0.001)

if __name__=="__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--overrides")
    a = ap.parse_args()
    main(a.config, a.overrides)
