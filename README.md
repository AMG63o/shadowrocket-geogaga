# Shadowrocket GeoGaGa

Автоматически обновляемые rule-set для Shadowrocket напрямую из всей ветки `lists` исходного репозитория `bratishkadrugoimamysynishka/geogaga-client-flavor`.

## Источник

Репозиторий-источник не ограничивается RunetFreedom или одним Client-Flavor. Workflow клонирует всю ветку `lists` и обрабатывает все каталоги, оканчивающиеся на `-geosite` и `-geoip`.

В исходной ветке есть `Client-Flavor-geosite`, `Client-Flavor-geoip`, `Loyalsoldier-*`, `b4-geoip`, `roscomvpn-*`, `runetfreedom-*` и другие наборы.

## Структура

Каталоги источника сохраняются один в один внутри `rules/`, а каждое `.lst` преобразуется в `.list`.

Например:

```text
Источник:
Client-Flavor-geosite/GEOGAGA-PROXY.lst

Результат:
rules/Client-Flavor-geosite/GEOGAGA-PROXY.list
```

И аналогично для всех остальных источников и файлов.

Для geosite поддерживаются `domain:`, `full:`, `keyword:` и `regex:`. Для geoip IPv4 преобразуется в `IP-CIDR`, IPv6 — в `IP-CIDR6`.

## Использование в Shadowrocket

Любой сгенерированный `.list` можно подключать как удалённый `RULE-SET`. Например:

```ini
[Rule]
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/Client-Flavor-geosite/GEOGAGA-BLOCK.list,REJECT
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/Client-Flavor-geosite/GEOGAGA-DIRECT.list,DIRECT
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/Client-Flavor-geosite/GEOGAGA-PROXY.list,PROXY
```

`PROXY` замени на название своей политики в Shadowrocket.

Полный список актуальных наборов и количества правил находится в `rules/meta.json`.

## Обновление

GitHub Actions клонирует свежую ветку `lists`, полностью пересобирает все исходные rule-set и публикует их в этом репозитории каждые 6 часов. Ручной запуск также доступен через Actions.
