# Shadowrocket GeoGaGa

Автоматически обновляемые rule-set для Shadowrocket непосредственно из ветки `lists` репозитория `bratishkadrugoimamysynishka/geogaga-client-flavor`.

## Источник

Используется именно `Client-Flavor-geosite` и `Client-Flavor-geoip`, а не RunetFreedom или другие сторонние наборы.

В исходном репозитории есть три категории:

- `GEOGAGA-DIRECT`
- `GEOGAGA-PROXY`
- `GEOGAGA-BLOCK`

Для geosite исходные записи `domain:`, `full:`, `keyword:` и `regex:` преобразуются в соответствующие правила Shadowrocket. Для geoip IPv4 преобразуется в `IP-CIDR`, IPv6 — в `IP-CIDR6`.

## Готовые rule-set

Geosite:

- `rules/geosite/GEOGAGA-DIRECT.list`
- `rules/geosite/GEOGAGA-PROXY.list`
- `rules/geosite/GEOGAGA-BLOCK.list`

GeoIP:

- `rules/geoip/GEOGAGA-DIRECT.list`
- `rules/geoip/GEOGAGA-PROXY.list`
- `rules/geoip/GEOGAGA-BLOCK.list`

## Raw URL

```text
https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geosite/GEOGAGA-DIRECT.list
https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geosite/GEOGAGA-PROXY.list
https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geosite/GEOGAGA-BLOCK.list

https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geoip/GEOGAGA-DIRECT.list
https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geoip/GEOGAGA-PROXY.list
https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geoip/GEOGAGA-BLOCK.list
```

## Shadowrocket

```ini
[Rule]
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geosite/GEOGAGA-BLOCK.list,REJECT
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geosite/GEOGAGA-DIRECT.list,DIRECT
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geosite/GEOGAGA-PROXY.list,PROXY
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geoip/GEOGAGA-BLOCK.list,REJECT
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geoip/GEOGAGA-DIRECT.list,DIRECT
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geoip/GEOGAGA-PROXY.list,PROXY
```

`PROXY` замени на название своей политики в Shadowrocket, если оно отличается.

## Обновление

GitHub Actions запускает сборку при изменениях в репозитории и автоматически каждые 6 часов. На каждом запуске берётся свежая ветка `lists`, а готовые rule-set полностью пересобираются.
