# Shadowrocket GeoGaGa

Автоматически обновляемые rule-set для Shadowrocket на основе списков GeoGaGa / RunetFreedom.

## Как это работает

GitHub Actions каждые 6 часов получает актуальные `.lst` из ветки `lists` репозитория GeoGaGa, преобразует их в синтаксис Shadowrocket и публикует готовые файлы в `rules/`.

Исходные geosite-файлы содержат записи вида `domain:example.com`; конвертер превращает их в `DOMAIN-SUFFIX,example.com`. GeoIP-префиксы CIDR превращаются в `IP-CIDR,...`.

## Rule-set для Shadowrocket

После первого запуска Actions доступны:

- `rules/runetfreedom-geosite.list` — доменные правила.
- `rules/runetfreedom-geoip.list` — IP/CIDR правила.

Raw URL для geosite:

`https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/runetfreedom-geosite.list`

Raw URL для geoip:

`https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/runetfreedom-geoip.list`

## Пример правил Shadowrocket

В секции `[Rule]`:

`RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/runetfreedom-geosite.list,PROXY`

`RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/runetfreedom-geoip.list,PROXY`

Замените `PROXY` на название вашей политики в Shadowrocket, если оно отличается.

## Обновление

Workflow запускается автоматически каждые 6 часов и также может быть запущен вручную через GitHub Actions.

Важно: GitHub Actions обновляет только файлы, которые реально изменились. Списки не редактируются вручную.
