[![StandWithUkraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua/)

<p align="center">
  <img src="custom_components/unit3d_stats/brand/icon.png" alt="UNIT3D Stats" width="128" />
</p>

<h1 align="center">UNIT3D Stats</h1>

<p align="center">

[![Validate](https://github.com/samokisha/ha-unit3d-stats/actions/workflows/validate.yml/badge.svg)](https://github.com/samokisha/ha-unit3d-stats/actions/workflows/validate.yml)
[![Lint](https://github.com/samokisha/ha-unit3d-stats/actions/workflows/lint.yml/badge.svg)](https://github.com/samokisha/ha-unit3d-stats/actions/workflows/lint.yml)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/samokisha/ha-unit3d-stats?display_name=tag&sort=semver)](https://github.com/samokisha/ha-unit3d-stats/releases)
[![License](https://img.shields.io/github/license/samokisha/ha-unit3d-stats)](./LICENSE)

</p>

> [!NOTE]
> Ця інтеграція не пов'язана з UNIT3D чи будь-яким конкретним трекером. Вона зчитує лише статистику вашого власного профілю через REST API трекера.

> [!TIP]
> Documentation is also available in [English 🇬🇧](./README.md).

Кастомна інтеграція для Home Assistant, яка опитує API-ендпоінт приватного трекера на движку UNIT3D і надає статистику вашого профілю у вигляді сенсорів, включно зі статистикою завантаження/вивантаження, активністю роздачі та іншим.

## Огляд

Ця інтеграція підключається до приватного трекера на движку [UNIT3D](https://github.com/HDInnovations/UNIT3D), використовуючи ваш особистий API-токен, та отримує статистику вашого акаунта. Кожен показник представлений як окремий сенсор, що дозволяє відстежувати активність на трекері, запускати автоматизації або створювати дашборди на основі вашого рейтингу, обсягів передачі даних, активності роздачі та інших показників профілю.

## Отримання API-ключа

Щоб користуватися цією інтеграцією, вам потрібен API-ключ вашого трекера на UNIT3D:

1. Увійдіть у свій акаунт трекера через браузер
2. Перейдіть у **Налаштування** (зазвичай доступні через меню профілю)
3. Знайдіть розділ **API Key**
4. Скопіюйте свій API-ключ

**Тримайте свій API-ключ у секреті** — ставтеся до нього як до пароля. Не діліться ним і не додавайте його в систему контролю версій.

## Встановлення

### Варіант A: HACS (рекомендовано)

1. Натисніть кнопку нижче, щоб відкрити HACS і додати цей репозиторій:

   [![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=samokisha&repository=ha-unit3d-stats&category=integration)

2. Встановіть інтеграцію **UNIT3D Stats** через HACS, після чого перезапустіть Home Assistant.
3. Натисніть кнопку нижче, щоб почати додавання інтеграції:

   [![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=unit3d_stats)

#### Ручне додавання кастомного репозиторію в HACS

Якщо кнопка вище не спрацювала у вашому налаштуванні:

1. Відкрийте **HACS → Integrations**
2. Натисніть меню з трьома крапками у верхньому правому куті → **Custom repositories**
3. Додайте `https://github.com/samokisha/ha-unit3d-stats` з категорією **Integration**
4. Знайдіть і встановіть **UNIT3D Stats**, після чого перезапустіть Home Assistant

### Варіант B: Ручне встановлення

1. Завантажте або клонуйте репозиторій [`ha-unit3d-stats`](https://github.com/samokisha/ha-unit3d-stats)
2. Скопіюйте директорію `custom_components/unit3d_stats` у папку `config/custom_components/` вашого Home Assistant
   - Типовий шлях: `~/.homeassistant/custom_components/unit3d_stats`
3. Перезапустіть Home Assistant

### Крок 2: Додавання інтеграції

1. Перейдіть у **Settings → Devices & Services**
2. Натисніть **Add Integration**
3. Знайдіть **"UNIT3D Stats"** і виберіть її
4. Введіть **Tracker Base URL** (наприклад, `https://tracker.example.com`)
5. Введіть свій **API Token** (з Кроку 1 вище)
6. Натисніть **Submit**

Інтеграція перевірить ваші облікові дані та створить запис. Набір сенсорів буде автоматично виявлений і стане доступним у Home Assistant.

## Сенсори

Інтеграція надає такі сенсори з профілю вашого трекера:

| Сенсор | Ключ | Одиниця | Тип | Опис |
|--------|-----|------|------|-------------|
| Group | `group` | — | Text | Ваша поточна група членства на трекері (наприклад, `Member`, `Uploader`) |
| Ratio | `ratio` | — | Measurement | Співвідношення вивантаженого до завантаженого (наприклад, 50.0 = 50:1) |
| Uploaded | `uploaded` | GiB | Total Increasing | Загальний обсяг вивантажених даних |
| Downloaded | `downloaded` | GiB | Total Increasing | Загальний обсяг завантажених даних |
| Buffer | `buffer` | GiB | Measurement | Доступний бонусний буфер/кредит |
| Seeding | `seeding` | — | Measurement | Кількість релізів, що зараз роздаються |
| Leeching | `leeching` | — | Measurement | Кількість релізів, що зараз завантажуються |
| Seed Bonus | `seedbonus` | — | Measurement | Накопичені бонусні очки за роздачу |
| Hit & Runs | `hit_and_runs` | — | Measurement | Кількість порушень hit-and-run |

Усі числові значення оновлюються з певним інтервалом (див. розділ Параметри нижче).

## Параметри

Після додавання інтеграції ви можете налаштувати інтервал оновлення:

1. Перейдіть у **Settings → Devices & Services** і знайдіть свій запис UNIT3D Stats
2. Натисніть **Configure**
3. Встановіть **Update Interval** (у хвилинах; за замовчуванням 60 хвилин)
4. Натисніть **Submit**

Інтеграція враховує обмеження швидкості трекера, використовуючи за замовчуванням інтервал опитування в 1 годину. Налаштуйте за потреби, але уникайте занадто частих оновлень, щоб не потрапити під обмеження швидкості трекера.

## Локальна розробка

### Налаштування

Щоб налаштувати середовище розробки:

```bash
./scripts/setup
```

Це встановить усі необхідні залежності.

### Запуск з тестовими даними

Для тестування без звернення до реального API трекера:

```bash
UNIT3D_MOCK=1 ./scripts/develop
```

Це запускає Home Assistant на `http://localhost:8123` з тестовими даними, завантаженими з файлу-фікстури інтеграції (`custom_components/unit3d_stats/fixtures/user_response.json`). У цьому режимі:
- Ви можете використовувати будь-який URL трекера та API-токен у формі налаштування
- Жодних реальних HTTP-запитів до трекера не виконується
- Немає впливу на ліміти швидкості
- Корисно для тестування інтерфейсу та розробки

### Запуск з реальним API

Щоб протестувати з реальним трекером:

```bash
./scripts/develop
```

Це запускає Home Assistant з використанням реального API трекера. Вам знадобиться дійсний URL трекера та API-токен.

### Лінтинг

Запустіть перевірку якості коду:

```bash
./scripts/lint
```

Це використовує `ruff` для перевірки форматування та стилю коду.

## Примітки

- **Тільки особиста статистика**: API-ендпоінт повертає статистику лише для власника акаунта, пов'язаного з API-токеном. Ви не можете використовувати цю інтеграцію для відстеження акаунтів інших користувачів.
- **Обмеження швидкості**: Інтервал оновлення за замовчуванням становить 1 годину, щоб враховувати обмеження швидкості трекера. Якщо ви стикаєтеся з помилками обмеження швидкості, збільшіть інтервал.
- **HTTP проти HTTPS**: URL трекера має використовувати `https`. Простий `http` приймається автоматично лише для локальних/довірених хостів (LAN, loopback, Tailscale); для публічної `http`-адреси потрібно позначити опцію **Allow HTTP without TLS** у формі налаштування.
- **HACS**: Ця інтеграція доступна як кастомний репозиторій HACS (див. розділ Встановлення вище). Вона ще не входить до стандартного магазину HACS.

## Усунення несправностей

### Недійсний API-токен

Якщо ви бачите помилку "Invalid API token", переконайтеся, що:
- Ваш API-ключ правильно скопійований з налаштувань трекера (включно з будь-якими пробілами чи спеціальними символами)
- Ваш акаунт трекера все ще активний
- API-ключ не був відкликаний

### Не вдається підключитися до трекера

Якщо ви бачите помилку підключення:
- Перевірте, що базовий URL трекера правильний (наприклад, `https://tracker.example.com` без завершального слеша)
- Переконайтеся, що трекер онлайн і доступний з вашого екземпляра Home Assistant
- Переконайтеся, що ваша мережа або файрвол не блокують вихідні HTTPS-запити до трекера
- Якщо ви використовуєте звичайний `http` URL для нелокального хоста, позначте опцію **Allow HTTP without TLS** у формі налаштування, або перейдіть на `https`

### Сенсори не з'являються

Після додавання інтеграції:
- Перейдіть у **Settings → Devices & Services** і перевірте, що інтеграція показує статус "Loaded"
- Перевірте логи Home Assistant на наявність повідомлень про помилки від компонента `custom_components.unit3d_stats`
- Спробуйте перезапустити Home Assistant

## Внесок у розробку

Ми раді будь-якому внеску! Будь ласка, переконайтеся, що всі зміни проходять лінтинг (`scripts/lint`) і наявні тести перед тим, як створювати pull request.
</content>
