# Shadowrocket GeoGaGa

Автоматически обновляемые rule-set для Shadowrocket напрямую из всей ветки `lists` исходного репозитория `bratishkadrugoimamysynishka/geogaga-client-flavor`.

## Оригинальный репозиторий

[GeoGaGa Client-Flavor — оригинальный репозиторий](https://github.com/bratishkadrugoimamysynishka/geogaga-client-flavor)

Используется именно ветка `lists`:

https://github.com/bratishkadrugoimamysynishka/geogaga-client-flavor/tree/lists

## Источник

Репозиторий-источник не ограничивается RunetFreedom или одним Client-Flavor. Workflow клонирует всю ветку `lists` и обрабатывает все каталоги, оканчивающиеся на `-geosite` и `-geoip`.

В исходной ветке есть `Client-Flavor-geosite`, `Client-Flavor-geoip`, `Loyalsoldier-*`, `b4-geoip`, `roscomvpn-*`, `runetfreedom-*` и другие наборы.

## Структура

Каталоги источника сохраняются один в один внутри `rules/`, а каждое `.lst` преобразуется в `.list`.

Например, в текущей структуре репозитория:

```text
Источник:
geogaga-client-flavor-geosite/GEOGAGA-PROXY.lst

Результат:
rules/geogaga-client-flavor-geosite/GEOGAGA-PROXY.list
```

И аналогично для всех остальных источников и файлов.

Для geosite поддерживаются `domain:`, `full:`, `keyword:` и `regex:`. Для geoip IPv4 преобразуется в `IP-CIDR`, IPv6 — в `IP-CIDR6`.

## Использование в Shadowrocket

Этот набор правил предполагается использовать **совместно** с конфигурацией из репозитория:

https://github.com/misha-tgshv/shadowrocket-configuration-file

В качестве базовых правил используются:

- [`sr_ru_geo.conf`](https://raw.githubusercontent.com/misha-tgshv/shadowrocket-configuration-file/refs/heads/main/conf/sr_ru_geo.conf) — базовые правила геомаршрутизации для РФ.
- [`sr_ru_extended.conf`](https://raw.githubusercontent.com/misha-tgshv/shadowrocket-configuration-file/refs/heads/main/conf/sr_ru_extended.conf) — файл для дополнительных пользовательских и кастомных правил.

Рекомендуемая схема: базовые правила оставлять в `sr_ru_geo.conf`, а свои дополнительные правила и подключение необходимых GeoGaGa `RULE-SET` добавлять в `sr_ru_extended.conf`. Это позволяет сохранять базовую конфигурацию отдельно и не смешивать её с пользовательскими правилами.

Любой сгенерированный `.list` можно подключать как удалённый `RULE-SET`. Ниже — готовый пример для пяти основных наборов GeoGaGa: три доменных списка и два IP-списка.

### Готовый фрагмент конфигурации

Добавь блок в секцию `[Rule]` своей конфигурации или в пользовательский файл `sr_ru_extended.conf`:

```ini
[Rule]
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geogaga-client-flavor-geosite/GEOGAGA-BLOCK.list,REJECT
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geogaga-client-flavor-geosite/GEOGAGA-DIRECT.list,DIRECT
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geogaga-client-flavor-geosite/GEOGAGA-PROXY.list,PROXY
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geogaga-client-flavor-geoip/GEOGAGA-DIRECT.list,DIRECT,no-resolve
RULE-SET,https://raw.githubusercontent.com/AMG63o/shadowrocket-geogaga/main/rules/geogaga-client-flavor-geoip/GEOGAGA-PROXY.list,PROXY,no-resolve
FINAL,PROXY
```

**Политики:**
- `REJECT` — отклонять соединения, совпавшие с набором блокировки.
- `DIRECT` — подключаться напрямую.
- `PROXY` — использовать прокси-политику. Если в твоём конфиге она называется иначе, замени `PROXY` на фактическое имя группы/политики.
- `no-resolve` для GeoIP-правил не позволяет выполнять DNS-разрешение домена только ради проверки IP-правила.

**Порядок правил важен:** Shadowrocket применяет первое совпавшее правило. Размещай эти строки с учётом уже существующих правил в своей конфигурации, а `FINAL,PROXY` оставляй в конце секции `[Rule]`. Если в конфиге уже есть секция `[Rule]`, не создавай вторую — добавь строки в существующую секцию.

Списки автоматически обновляются в этом репозитории, поэтому после подключения удалённых `RULE-SET` вручную обновлять их содержимое не нужно.

Полный список актуальных наборов и количества правил находится в `rules/meta.json`.

## Обновление

GitHub Actions автоматически запускается **каждые 6 часов** (`00:17, 06:17, 12:17 и 18:17 UTC`), клонирует свежую ветку `lists`, полностью пересобирает все исходные rule-set и публикует изменения в этом репозитории. Ручной запуск также доступен через Actions.

Таким образом, после добавления нужного `RULE-SET` в `sr_ru_extended.conf` вручную обновлять списки в этом репозитории не требуется.