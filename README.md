# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/kyamano/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/kyamano/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A program that draws one 1024x1024 image summing up the world news of
Sunday, 22 November 2026: COP31 climate talks collapse with no deal, Ukraine
sinks a Russian warship off Libya, Russian strikes kill 14 in the Kyiv
region, tankers are hit near the Strait of Hormuz, Mexico captures cartel
kingpin "Chapo Isidro", a boat capsizes in Nigeria, a factory fire in
Indonesia, the US presses Nvidia over AI chips sold to China, Trump signals
openness to Article 5-style guarantees for Ukraine, and Okinawa's Shuri
Castle rises again — plus twenty more stories from the day.

The picture is drawn from scratch with a tiny built-in rasterizer and a 5x7
bitmap font, using only the Python standard library, so it runs with no
network and no installed packages. Running it twice writes byte-identical
PNGs. See [the bounty page](https://make.fun/bounty/news-image-20261122)
for the competition.

## Run it

```sh
python3 main.py
```

This writes `entry.png` (1024x1024, under 1 MiB) to `$MAKEFUN_OUTPUT_DIR`,
or `/output` when that is unset.

---

Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards
