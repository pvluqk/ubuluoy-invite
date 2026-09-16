# Хостинг и домен

## Важно про домен

**Без входа в Reg.ru домен `yuliaegorovna.ru` привязать нельзя** — DNS меняются только там.

Пока VPN мешает войти:
1. Выключи VPN на час
2. Зайди в Reg.ru
3. Привяжем домен за 5 минут

Пока пользуйся рабочей ссылкой Render:
- Приглашение: https://ubuluoy-invite.onrender.com/
- Гости: https://ubuluoy-invite.onrender.com/guests?key=ubuluoy-secret-2026

Экран «APPLICATION LOADING» — это бесплатный Render «просыпается» (~30–60 сек).

---

## Вариант: Railway (меньше «сна», если выключить Serverless)

1. Зайди на [railway.app](https://railway.app) → Sign up через **GitHub** (`pvluqk`)
2. **New Project** → **Deploy from GitHub repo**
3. Выбери `ubuluoy-invite` → Deploy
4. Settings → **Networking** → **Generate Domain**
5. Settings → **Serverless / App Sleeping** → **выключи** (иначе опять будет засыпать)
6. Variables добавь:
   - `ADMIN_KEY` = `ubuluoy-secret-2026`
   - `EVENT_ISO` = `2026-10-04T14:00:00+09:00`

Бесплатного кредита мало (~$1/мес). Для юбилея удобнее **Hobby $5/мес** — сайт стабильнее.

---

## Когда зайдёшь в Reg.ru (домен)

В DNS для `yuliaegorovna.ru`:

| Тип | Имя | Значение |
|-----|-----|----------|
| A | `@` | IP или значение с хостинга |
| CNAME | `www` | адрес сервиса (`.onrender.com` или `.up.railway.app`) |

Точные значения покажет хостинг в Custom Domains.

---

## Ссылки после всего

| Кому | URL |
|------|-----|
| Гостям | `https://yuliaegorovna.ru/` |
| Организаторам | `https://yuliaegorovna.ru/guests?key=ubuluoy-secret-2026` |
