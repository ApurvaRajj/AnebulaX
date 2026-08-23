# AnebulaX — Complete Command & Intent Reference Manual

This reference contains the **complete, exhaustive directory of all 747 native executors** and all **1371 registered trigger word-sets** supported by AnebulaX.

AnebulaX uses word-set intersection scoring. Any listed trigger words spoken in any order (with or without conjunctions like *and* or *then*) will automatically route to the corresponding executor.

---

## ⚙️ System Configuration & Diagnostics (20 Executors)

| # | Executor Identifier | Natural Trigger Word Sets | Description / Action |
|---|---|---|---|
| 1 | `cfg_list_mics` | • <code>[list, mics]</code><br>• <code>[list, microphones]</code><br>• <code>[mics, show]</code><br>• <code>[list, mic]</code> | Cfg list mics |
| 2 | `cfg_set_ai` | • <code>[ai, set]</code> | Cfg set ai |
| 3 | `cfg_set_api_key` | • <code>[api, key, set]</code> | Cfg set api key |
| 4 | `cfg_set_browser` | • <code>[browser, set]</code> | Cfg set browser |
| 5 | `cfg_set_dynamic` | • <code>[dynamic, set]</code><br>• <code>[dynamic, on]</code><br>• <code>[dynamic, off]</code><br>• <code>[dynamic, toggle]</code><br>• <code>[dynamic, energy]</code><br>• <code>[dynamic, threshold]</code> | Cfg set dynamic |
| 6 | `cfg_set_energy` | • <code>[energy, set]</code> | Cfg set energy |
| 7 | `cfg_set_mic` | • <code>[mic, set]</code><br>• <code>[microphone, set]</code> | Cfg set mic |
| 8 | `cfg_set_search` | • <code>[search, set]</code> | Cfg set search |
| 9 | `cfg_set_stt` | • <code>[set, stt]</code><br>• <code>[google, set, stt]</code><br>• <code>[set, stt, vosk]</code><br>• <code>[offline, set, stt]</code><br>• <code>[online, set, stt]</code><br>• <code>[auto, set, stt]</code> | Cfg set stt |
| 10 | `cfg_set_theme` | • <code>[set, theme]</code> | Cfg set theme |
| 11 | `cfg_show` | • <code>[config, show]</code><br>• <code>[settings]</code> | Cfg show |
| 12 | `cfg_show_ai` | • <code>[ai, default]</code> | Cfg show ai |
| 13 | `cfg_show_stt` | • <code>[status, stt]</code><br>• <code>[show, stt]</code> | Cfg show stt |
| 14 | `cfg_test_mic` | • <code>[mic, test]</code><br>• <code>[microphone, test]</code><br>• <code>[mic, test]</code><br>• <code>[doctor, voice]</code><br>• <code>[diagnostic, voice]</code><br>• <code>[test, voice]</code><br>• <code>[test, voice]</code><br>• <code>[speech, test]</code><br>• <code>[stt, test]</code><br>• <code>[diagnose, mic]</code><br>• <code>[diagnose, voice]</code> | Cfg test mic |
| 15 | `cfg_toggle_nebula_tts` | • <code>[mute, nebula]</code><br>• <code>[nebula, voice]</code><br>• <code>[nebula, speech, toggle]</code> | Cfg toggle nebula tts |
| 16 | `cfg_toggle_nova_confirm` | • <code>[confirm, nova]</code><br>• <code>[auto, nova]</code> | Cfg toggle nova confirm |
| 17 | `cfg_toggle_nova_tts` | • <code>[mute, nova]</code><br>• <code>[nova, voice]</code><br>• <code>[nova, speech, toggle]</code> | Cfg toggle nova tts |
| 18 | `cfg_toggle_stt` | • <code>[stt, toggle]</code><br>• <code>[stt, switch]</code> | Cfg toggle stt |
| 19 | `cfg_toggle_tts` | • <code>[toggle, tts]</code><br>• <code>[toggle, voice]</code><br>• <code>[mute, voice]</code><br>• <code>[unmute, voice]</code><br>• <code>[output, voice]</code> | Cfg toggle tts |
| 20 | `cfg_toggle_yolo` | • <code>[toggle, yolo]</code> | Cfg toggle yolo |

---

## 🌐 Web Navigation, Browsing & Application Launchers (127 Executors)

| # | Executor Identifier | Natural Trigger Word Sets | Description / Action |
|---|---|---|---|
| 21 | `a2_android_studio` | • <code>[android, open, studio]</code> | A2 android studio |
| 22 | `a2_audacity` | • <code>[audacity, open]</code><br>• <code>[audacity]</code> | A2 audacity |
| 23 | `a2_canva` | • <code>[canva]</code><br>• <code>[canva, open]</code> | A2 canva |
| 24 | `a2_colab` | • <code>[colab]</code> | A2 colab |
| 25 | `a2_dbeaver` | • <code>[dbeaver, open]</code> | A2 dbeaver |
| 26 | `a2_discord` | • <code>[discord, open]</code><br>• <code>[discord]</code> | A2 discord |
| 27 | `a2_figma` | • <code>[figma]</code><br>• <code>[figma, open]</code> | A2 figma |
| 28 | `a2_gimp` | • <code>[gimp, open]</code><br>• <code>[gimp]</code> | A2 gimp |
| 29 | `a2_jira` | • <code>[jira, open]</code> | A2 jira |
| 30 | `a2_mail` | • <code>[mail, open]</code> | A2 mail |
| 31 | `a2_maps` | • <code>[maps, open]</code><br>• <code>[google, maps]</code> | A2 maps |
| 32 | `a2_music` | • <code>[music, open]</code> | A2 music |
| 33 | `a2_notion` | • <code>[notion, open]</code> | A2 notion |
| 34 | `a2_nvim` | • <code>[neovim]</code><br>• <code>[nvim]</code> | A2 nvim |
| 35 | `a2_obs` | • <code>[obs, open]</code><br>• <code>[obs]</code> | A2 obs |
| 36 | `a2_obsidian` | • <code>[obsidian, open]</code> | A2 obsidian |
| 37 | `a2_photos` | • <code>[open, photos]</code> | A2 photos |
| 38 | `a2_postman` | • <code>[postman]</code><br>• <code>[open, postman]</code> | A2 postman |
| 39 | `a2_replit` | • <code>[replit]</code> | A2 replit |
| 40 | `a2_slack` | • <code>[open, slack]</code><br>• <code>[slack]</code><br>• <code>[open, slack]</code> | A2 slack |
| 41 | `a2_teams` | • <code>[open, teams]</code> | A2 teams |
| 42 | `a2_telegram` | • <code>[open, telegram]</code><br>• <code>[telegram]</code><br>• <code>[open, telegram]</code> | A2 telegram |
| 43 | `a2_whatsapp` | • <code>[whatsapp]</code><br>• <code>[open, whatsapp]</code> | A2 whatsapp |
| 44 | `a2_zoom` | • <code>[open, zoom]</code><br>• <code>[zoom]</code><br>• <code>[open, zoom]</code> | A2 zoom |
| 45 | `app_brave` | • <code>[brave, open]</code><br>• <code>[brave, browser]</code> | App brave |
| 46 | `app_calc` | • <code>[calculator]</code><br>• <code>[calculator, open]</code> | App calc |
| 47 | `app_chrome` | • <code>[chrome, open]</code><br>• <code>[chrome, launch]</code><br>• <code>[chrome]</code> | App chrome |
| 48 | `app_close` | • <code>[app, close]</code><br>• <code>[app, quit]</code> | App close |
| 49 | `app_edge` | • <code>[edge, open]</code><br>• <code>[edge, microsoft]</code> | App edge |
| 50 | `app_excel` | • <code>[excel, open]</code><br>• <code>[excel, microsoft]</code> | App excel |
| 51 | `app_explorer` | • <code>[file, manager]</code><br>• <code>[explorer, file]</code> | App explorer |
| 52 | `app_firefox` | • <code>[firefox, open]</code><br>• <code>[firefox]</code> | App firefox |
| 53 | `app_notepad` | • <code>[notepad]</code><br>• <code>[editor, text]</code> | App notepad |
| 54 | `app_paint` | • <code>[paint]</code> | App paint |
| 55 | `app_settings` | • <code>[settings, system]</code><br>• <code>[preferences]</code> | App settings |
| 56 | `app_spotify` | • <code>[open, spotify]</code><br>• <code>[spotify]</code> | App spotify |
| 57 | `app_terminal` | • <code>[terminal]</code><br>• <code>[open, terminal]</code><br>• <code>[command, prompt]</code> | App terminal |
| 58 | `app_vlc` | • <code>[open, vlc]</code><br>• <code>[vlc]</code> | App vlc |
| 59 | `app_vscode` | • <code>[open, vscode]</code><br>• <code>[vscode]</code><br>• <code>[code, studio, visual]</code> | App vscode |
| 60 | `app_word` | • <code>[open, word]</code><br>• <code>[microsoft, word]</code> | App word |
| 61 | `b2_devdocs` | • <code>[devdocs]</code> | B2 devdocs |
| 62 | `b2_linkedin` | • <code>[linkedin]</code> | B2 linkedin |
| 63 | `b2_mdn` | • <code>[mdn]</code> | B2 mdn |
| 64 | `b2_notion` | • <code>[notion]</code><br>• <code>[notion, open]</code> | B2 notion |
| 65 | `b2_pypi` | • <code>[pypi]</code> | B2 pypi |
| 66 | `b2_regex` | • <code>[regex101]</code> | B2 regex |
| 67 | `b2_response_time` | • <code>[response, time]</code><br>• <code>[site, speed]</code> | B2 response time |
| 68 | `b2_stackoverflow` | • <code>[stackoverflow]</code><br>• <code>[overflow, stack]</code> | B2 stackoverflow |
| 69 | `b2_translate` | • <code>[translate]</code><br>• <code>[google, translate]</code><br>• <code>[open, translate]</code> | B2 translate |
| 70 | `b2_translate_text` | • <code>[translate]</code> | B2 translate text |
| 71 | `b2_trello` | • <code>[trello]</code><br>• <code>[open, trello]</code> | B2 trello |
| 72 | `b2_twitter` | • <code>[twitter]</code><br>• <code>[x.com]</code> | B2 twitter |
| 73 | `b2_webcheck` | • <code>[check, web]</code> | B2 webcheck |
| 74 | `bc_back` | • <code>[back, go]</code><br>• <code>[back, browser]</code><br>• <code>[page, previous]</code> | Bc back |
| 75 | `bc_bookmark` | • <code>[bookmark, page]</code><br>• <code>[bookmark, save]</code> | Bc bookmark |
| 76 | `bc_close_tab` | • <code>[close, tab]</code><br>• <code>[close, tab, this]</code> | Bc close tab |
| 77 | `bc_downloads` | • <code>[downloads, show]</code><br>• <code>[browser, downloads]</code> | Bc downloads |
| 78 | `bc_forward` | • <code>[forward, go]</code><br>• <code>[browser, forward]</code><br>• <code>[next, page]</code> | Bc forward |
| 79 | `bc_history` | • <code>[history, show]</code><br>• <code>[browser, history]</code> | Bc history |
| 80 | `bc_new_tab` | • <code>[new, tab]</code><br>• <code>[new, open, tab]</code><br>• <code>[switch, tab]</code><br>• <code>[next, tab]</code> | Bc new tab |
| 81 | `bc_page_down` | • <code>[down, page]</code> | Bc page down |
| 82 | `bc_page_up` | • <code>[page, up]</code> | Bc page up |
| 83 | `bc_refresh` | • <code>[refresh, tab]</code><br>• <code>[reload, tab]</code><br>• <code>[page, refresh]</code><br>• <code>[page, reload]</code> | Bc refresh |
| 84 | `bc_reopen_tab` | • <code>[reopen, tab]</code><br>• <code>[page, reopen]</code> | Bc reopen tab |
| 85 | `web_amazon_search` | • <code>[amazon, search]</code> | Web amazon search |
| 86 | `web_asana` | • <code>[asana]</code> | Web asana |
| 87 | `web_ask_chatgpt` | • <code>[chatgpt, search]</code><br>• <code>[ask, chatgpt]</code> | Web ask chatgpt |
| 88 | `web_ask_claude` | • <code>[claude, search]</code><br>• <code>[ask, claude]</code> | Web ask claude |
| 89 | `web_ask_default_ai` | • <code>[ai, ask]</code> | Web ask default ai |
| 90 | `web_ask_gemini` | • <code>[gemini, search]</code><br>• <code>[ask, gemini]</code> | Web ask gemini |
| 91 | `web_ask_perplexity` | • <code>[perplexity, search]</code><br>• <code>[ask, perplexity]</code> | Web ask perplexity |
| 92 | `web_aws` | • <code>[aws, console]</code> | Web aws |
| 93 | `web_azure` | • <code>[azure]</code> | Web azure |
| 94 | `web_bbc` | • <code>[bbc, news]</code> | Web bbc |
| 95 | `web_bing` | • <code>[bing]</code> | Web bing |
| 96 | `web_chatgpt` | • <code>[chatgpt, open]</code><br>• <code>[chatgpt]</code> | Web chatgpt |
| 97 | `web_claude` | • <code>[claude, open]</code> | Web claude |
| 98 | `web_codepen` | • <code>[codepen]</code> | Web codepen |
| 99 | `web_codesandbox` | • <code>[codesandbox]</code> | Web codesandbox |
| 100 | `web_codewars` | • <code>[codewars]</code> | Web codewars |
| 101 | `web_ddg` | • <code>[duckduckgo]</code> | Web ddg |
| 102 | `web_devto` | • <code>[devto]</code> | Web devto |
| 103 | `web_dictionary` | • <code>[define, word]</code><br>• <code>[dictionary]</code><br>• <code>[define]</code> | Web dictionary |
| 104 | `web_drive` | • <code>[drive, google]</code> | Web drive |
| 105 | `web_exercism` | • <code>[exercism]</code> | Web exercism |
| 106 | `web_gcal` | • <code>[calendar, open]</code> | Web gcal |
| 107 | `web_gdocs` | • <code>[docs, google]</code> | Web gdocs |
| 108 | `web_gh_trending` | • <code>[github, trending]</code> | Web gh trending |
| 109 | `web_github` | • <code>[github, open]</code><br>• <code>[github]</code> | Web github |
| 110 | `web_github_search` | • <code>[github, search]</code> | Web github search |
| 111 | `web_gmail` | • <code>[gmail, open]</code><br>• <code>[gmail]</code> | Web gmail |
| 112 | `web_google` | • <code>[google]</code> | Web google |
| 113 | `web_gsheets` | • <code>[google, sheets]</code> | Web gsheets |
| 114 | `web_gslides` | • <code>[open, slides]</code> | Web gslides |
| 115 | `web_hackerrank` | • <code>[hackerrank]</code> | Web hackerrank |
| 116 | `web_hn` | • <code>[hacker, news]</code> | Web hn |
| 117 | `web_images` | • <code>[image, search]</code><br>• <code>[images, search]</code><br>• <code>[google, images]</code> | Web images |
| 118 | `web_jira` | • <code>[jira]</code> | Web jira |
| 119 | `web_leetcode` | • <code>[leetcode]</code> | Web leetcode |
| 120 | `web_maps` | • <code>[maps]</code><br>• <code>[google, maps]</code> | Web maps |
| 121 | `web_medium` | • <code>[medium]</code> | Web medium |
| 122 | `web_meet` | • <code>[meet, open]</code> | Web meet |
| 123 | `web_messages` | • <code>[messages, web]</code><br>• <code>[google, messages]</code><br>• <code>[messages, open]</code> | Web messages |
| 124 | `web_netflix` | • <code>[netflix, open]</code><br>• <code>[netflix]</code> | Web netflix |
| 125 | `web_netlify` | • <code>[netlify]</code> | Web netlify |
| 126 | `web_open_site_smart` | • <code>[go, to]</code><br>• <code>[goto]</code><br>• <code>[open, site]</code> | Web open site smart |
| 127 | `web_private` | • <code>[browser, private]</code><br>• <code>[incognito]</code><br>• <code>[private, window]</code><br>• <code>[private, tab]</code> | Web private |
| 128 | `web_reddit` | • <code>[open, reddit]</code><br>• <code>[reddit]</code> | Web reddit |
| 129 | `web_reddit_search` | • <code>[reddit, search]</code> | Web reddit search |
| 130 | `web_research` | • <code>[research]</code><br>• <code>[on, research]</code> | Web research |
| 131 | `web_scholar` | • <code>[scholar]</code><br>• <code>[google, scholar]</code> | Web scholar |
| 132 | `web_search` | • <code>[search]</code> | Web search |
| 133 | `web_search_incognito` | • <code>[incognito, search]</code><br>• <code>[incognito, search]</code><br>• <code>[private, search]</code> | Web search incognito |
| 134 | `web_soundcloud` | • <code>[soundcloud]</code> | Web soundcloud |
| 135 | `web_stackblitz` | • <code>[stackblitz]</code> | Web stackblitz |
| 136 | `web_techcrunch` | • <code>[techcrunch]</code> | Web techcrunch |
| 137 | `web_thesaurus` | • <code>[thesaurus]</code><br>• <code>[synonym]</code> | Web thesaurus |
| 138 | `web_theverge` | • <code>[the, verge]</code> | Web theverge |
| 139 | `web_trends` | • <code>[google, trends]</code> | Web trends |
| 140 | `web_twitch` | • <code>[open, twitch]</code> | Web twitch |
| 141 | `web_urban` | • <code>[dictionary, urban]</code> | Web urban |
| 142 | `web_url` | • <code>[open, url]</code> | Web url |
| 143 | `web_vercel` | • <code>[vercel]</code> | Web vercel |
| 144 | `web_wiki` | • <code>[wikipedia]</code><br>• <code>[wiki]</code><br>• <code>[open, wikipedia]</code> | Web wiki |
| 145 | `web_wired` | • <code>[wired]</code> | Web wired |
| 146 | `web_youtube` | • <code>[open, youtube]</code><br>• <code>[youtube]</code> | Web youtube |
| 147 | `web_yt_search` | • <code>[search, youtube]</code> | Web yt search |

---

## 🎉 Entertainment, Weather, News & Fun (42 Executors)

| # | Executor Identifier | Natural Trigger Word Sets | Description / Action |
|---|---|---|---|
| 148 | `fun_8ball` | • <code>[8, ball]</code><br>• <code>[ball, magic]</code> | Fun 8ball |
| 149 | `fun_affirm` | • <code>[affirmation]</code><br>• <code>[me, motivate]</code> | Fun affirm |
| 150 | `fun_coin` | • <code>[coin]</code><br>• <code>[coin, flip]</code><br>• <code>[heads, tails]</code><br>• <code>[coin, flip]</code><br>• <code>[heads, tails]</code> | Fun coin |
| 151 | `fun_compliment` | • <code>[compliment]</code> | Fun compliment |
| 152 | `fun_cowsay` | • <code>[cowsay]</code> | Fun cowsay |
| 153 | `fun_dice` | • <code>[dice, roll]</code><br>• <code>[dice]</code><br>• <code>[roll]</code><br>• <code>[dice]</code> | Fun dice |
| 154 | `fun_fact` | • <code>[fact]</code><br>• <code>[fact, random]</code><br>• <code>[fact, fun]</code> | Fun fact |
| 155 | `fun_fortune` | • <code>[fortune]</code> | Fun fortune |
| 156 | `fun_greet` | • <code>[greet]</code><br>• <code>[hello]</code><br>• <code>[good, morning]</code><br>• <code>[afternoon, good]</code><br>• <code>[evening, good]</code> | Fun greet |
| 157 | `fun_haiku` | • <code>[haiku]</code> | Fun haiku |
| 158 | `fun_joke` | • <code>[joke]</code><br>• <code>[joke, tell]</code><br>• <code>[funny]</code><br>• <code>[dad, joke]</code> | Fun joke |
| 159 | `fun_magic8` | • <code>[8, magic]</code><br>• <code>[ball, eight]</code> | Fun magic8 |
| 160 | `fun_num_fact` | • <code>[fact, number]</code> | Fun num fact |
| 161 | `fun_poem` | • <code>[poem]</code> | Fun poem |
| 162 | `fun_quote` | • <code>[quote]</code><br>• <code>[inspire]</code><br>• <code>[motivation]</code> | Fun quote |
| 163 | `fun_rand_choice` | • <code>[choice, random]</code><br>• <code>[from, pick]</code> | Fun rand choice |
| 164 | `fun_rand_color` | • <code>[color, random]</code> | Fun rand color |
| 165 | `fun_rand_emoji` | • <code>[emoji, random]</code> | Fun rand emoji |
| 166 | `fun_rand_num` | • <code>[number, random]</code><br>• <code>[between, random]</code><br>• <code>[pick, random]</code> | Fun rand num |
| 167 | `fun_rand_word` | • <code>[random, word]</code> | Fun rand word |
| 168 | `fun_random_name` | • <code>[name, random]</code> | Fun random name |
| 169 | `fun_recipe` | • <code>[recipe]</code><br>• <code>[cooking]</code> | Fun recipe |
| 170 | `fun_riddle` | • <code>[riddle]</code> | Fun riddle |
| 171 | `fun_roast` | • <code>[me, roast]</code> | Fun roast |
| 172 | `fun_rps` | • <code>[paper, rock, scissors]</code> | Fun rps |
| 173 | `fun_shuffle` | • <code>[shuffle]</code> | Fun shuffle |
| 174 | `fun_story` | • <code>[story]</code> | Fun story |
| 175 | `fun_teaser` | • <code>[brain, teaser]</code> | Fun teaser |
| 176 | `fun_this_day` | • <code>[day, on, this]</code><br>• <code>[day, history, this]</code> | Fun this day |
| 177 | `fun_tongue` | • <code>[tongue, twister]</code> | Fun tongue |
| 178 | `fun_trivia` | • <code>[trivia]</code><br>• <code>[trivia]</code><br>• <code>[me, quiz]</code> | Fun trivia |
| 179 | `fun_word` | • <code>[day, word]</code><br>• <code>[day, of, word]</code> | Fun word |
| 180 | `fun_word_day` | • <code>[day, of, word]</code> | Fun word day |
| 181 | `fun_word_game` | • <code>[game, word]</code><br>• <code>[guess, word]</code> | Fun word game |
| 182 | `fun_wyr` | • <code>[rather, would, you]</code><br>• <code>[or, that, this]</code> | Fun wyr |
| 183 | `wn_crypto` | • <code>[crypto]</code><br>• <code>[bitcoin]</code> | Wn crypto |
| 184 | `wn_exchange` | • <code>[exchange, rate]</code><br>• <code>[currency]</code> | Wn exchange |
| 185 | `wn_ipinfo` | • <code>[info, ip]</code> | Wn ipinfo |
| 186 | `wn_moon_phase` | • <code>[moon, phase]</code><br>• <code>[moon]</code> | Wn moon phase |
| 187 | `wn_news` | • <code>[news]</code><br>• <code>[headlines]</code> | Wn news |
| 188 | `wn_stock` | • <code>[stock]</code> | Wn stock |
| 189 | `wn_weather` | • <code>[weather]</code><br>• <code>[forecast]</code> | Wn weather |

---

## 🎵 Media, Keyboard, Window & Desktop Control (81 Executors)

| # | Executor Identifier | Natural Trigger Word Sets | Description / Action |
|---|---|---|---|
| 190 | `clip_clear` | • <code>[clear, clipboard]</code><br>• <code>[clear, clipboard]</code> | Clip clear |
| 191 | `clip_copy_sel` | • <code>[copy]</code><br>• <code>[copy, selection]</code> | Clip copy sel |
| 192 | `clip_cut` | • <code>[cut]</code> | Clip cut |
| 193 | `clip_paste` | • <code>[paste]</code> | Clip paste |
| 194 | `edit_redo` | • <code>[redo]</code> | Edit redo |
| 195 | `edit_select_all` | • <code>[all, select]</code> | Edit select all |
| 196 | `edit_undo` | • <code>[undo]</code> | Edit undo |
| 197 | `m2_play_file` | • <code>[file, play]</code> | M2 play file |
| 198 | `m2_record_audio` | • <code>[audio, record]</code> | M2 record audio |
| 199 | `m2_record_screen` | • <code>[record, screen]</code><br>• <code>[record, screen]</code> | M2 record screen |
| 200 | `mm_add_bookmark` | • <code>[add, bookmark]</code><br>• <code>[add, bookmark]</code><br>• <code>[bookmark, save]</code> | Mm add bookmark |
| 201 | `mm_arrow_dn` | • <code>[arrow, down]</code><br>• <code>[down]</code> | Mm arrow dn |
| 202 | `mm_arrow_left` | • <code>[arrow, left]</code><br>• <code>[left]</code> | Mm arrow left |
| 203 | `mm_arrow_right` | • <code>[arrow, right]</code><br>• <code>[right]</code> | Mm arrow right |
| 204 | `mm_arrow_up` | • <code>[arrow, up]</code><br>• <code>[up]</code> | Mm arrow up |
| 205 | `mm_backspace` | • <code>[backspace, press]</code><br>• <code>[backspace]</code> | Mm backspace |
| 206 | `mm_close_window` | • <code>[close, window]</code><br>• <code>[close, this, window]</code><br>• <code>[active, close, window]</code> | Mm close window |
| 207 | `mm_copy` | • <code>[copy, selection]</code><br>• <code>[copy, that]</code><br>• <code>[copy, this]</code><br>• <code>[copy]</code> | Mm copy |
| 208 | `mm_cut` | • <code>[cut, selection]</code><br>• <code>[cut, that]</code><br>• <code>[cut, this]</code><br>• <code>[cut]</code> | Mm cut |
| 209 | `mm_del_bookmark` | • <code>[bookmark, delete]</code><br>• <code>[bookmark, remove]</code> | Mm del bookmark |
| 210 | `mm_delete_key` | • <code>[delete, press]</code> | Mm delete key |
| 211 | `mm_emoji` | • <code>[emoji, picker]</code> | Mm emoji |
| 212 | `mm_end_key` | • <code>[end, press]</code><br>• <code>[end]</code> | Mm end key |
| 213 | `mm_enter` | • <code>[enter, press]</code><br>• <code>[enter]</code> | Mm enter |
| 214 | `mm_escape` | • <code>[escape, press]</code><br>• <code>[escape]</code> | Mm escape |
| 215 | `mm_find_text` | • <code>[find, text]</code><br>• <code>[find, on, page]</code><br>• <code>[find, text]</code><br>• <code>[find, on, page]</code><br>• <code>[find, word]</code><br>• <code>[find, here]</code><br>• <code>[find]</code> | Mm find text |
| 216 | `mm_home_key` | • <code>[home, press]</code><br>• <code>[home]</code> | Mm home key |
| 217 | `mm_img_blur` | • <code>[blur, image]</code> | Mm img blur |
| 218 | `mm_img_compress` | • <code>[compress, image]</code> | Mm img compress |
| 219 | `mm_img_convert` | • <code>[convert, image]</code> | Mm img convert |
| 220 | `mm_img_crop` | • <code>[crop, image]</code> | Mm img crop |
| 221 | `mm_img_exif` | • <code>[exif]</code><br>• <code>[image, metadata]</code> | Mm img exif |
| 222 | `mm_img_flip` | • <code>[flip, image]</code> | Mm img flip |
| 223 | `mm_img_gray` | • <code>[grayscale, image]</code> | Mm img gray |
| 224 | `mm_img_info` | • <code>[image, info]</code> | Mm img info |
| 225 | `mm_img_ocr` | • <code>[ocr]</code> | Mm img ocr |
| 226 | `mm_img_resize` | • <code>[image, resize]</code> | Mm img resize |
| 227 | `mm_img_rotate` | • <code>[image, rotate]</code> | Mm img rotate |
| 228 | `mm_img_thumb` | • <code>[image, thumbnail]</code> | Mm img thumb |
| 229 | `mm_incognito_here` | • <code>[here, incognito]</code><br>• <code>[here, private]</code> | Mm incognito here |
| 230 | `mm_list_bookmarks` | • <code>[bookmarks, list]</code><br>• <code>[bookmarks, show]</code><br>• <code>[bookmarks, my]</code> | Mm list bookmarks |
| 231 | `mm_list_images` | • <code>[images, list]</code> | Mm list images |
| 232 | `mm_list_software` | • <code>[list, software]</code><br>• <code>[show, software]</code><br>• <code>[my, software]</code><br>• <code>[list, software]</code><br>• <code>[show, software]</code><br>• <code>[apps, registered]</code> | Mm list software |
| 233 | `mm_magnifier` | • <code>[magnifier]</code><br>• <code>[magnify]</code><br>• <code>[in, zoom]</code> | Mm magnifier |
| 234 | `mm_maximize_app` | • <code>[maximize]</code><br>• <code>[maximise]</code><br>• <code>[expand]</code> | Mm maximize app |
| 235 | `mm_minimize_app` | • <code>[minimize]</code><br>• <code>[minimise]</code> | Mm minimize app |
| 236 | `mm_next` | • <code>[next, track]</code><br>• <code>[next, song]</code> | Mm next |
| 237 | `mm_notification_center` | • <code>[center, notification]</code><br>• <code>[action, center]</code><br>• <code>[notifications]</code> | Mm notification center |
| 238 | `mm_open_bookmark` | • <code>[go, to]</code><br>• <code>[goto]</code> | Mm open bookmark |
| 239 | `mm_open_software` | • <code>[open, software]</code><br>• <code>[launch, software]</code> | Mm open software |
| 240 | `mm_page_dn` | • <code>[bottom, scroll]</code><br>• <code>[down, page]</code> | Mm page dn |
| 241 | `mm_page_up` | • <code>[scroll, top]</code><br>• <code>[page, up]</code> | Mm page up |
| 242 | `mm_paste` | • <code>[paste, that]</code><br>• <code>[it, paste]</code><br>• <code>[paste, this]</code><br>• <code>[paste]</code> | Mm paste |
| 243 | `mm_play` | • <code>[play]</code><br>• <code>[pause]</code> | Mm play |
| 244 | `mm_prev` | • <code>[previous, track]</code><br>• <code>[previous, song]</code> | Mm prev |
| 245 | `mm_read_aloud` | • <code>[aloud, read]</code> | Mm read aloud |
| 246 | `mm_read_clipboard` | • <code>[clipboard, read]</code><br>• <code>[clipboard, what]</code> | Mm read clipboard |
| 247 | `mm_read_selection` | • <code>[read, this]</code><br>• <code>[read, selection]</code><br>• <code>[read, that]</code><br>• <code>[highlighted, read]</code> | Mm read selection |
| 248 | `mm_redo` | • <code>[redo, that]</code><br>• <code>[redo]</code> | Mm redo |
| 249 | `mm_reopen_tab` | • <code>[reopen, tab]</code><br>• <code>[page, reopen]</code><br>• <code>[closed, reopen]</code><br>• <code>[restore, tab]</code> | Mm reopen tab |
| 250 | `mm_research` | • <code>[research]</code> | Mm research |
| 251 | `mm_restore_app` | • <code>[restore]</code><br>• <code>[restore, window]</code><br>• <code>[previous, window]</code><br>• <code>[app, previous]</code><br>• <code>[shrink]</code> | Mm restore app |
| 252 | `mm_scroll_dn` | • <code>[down, scroll]</code> | Mm scroll dn |
| 253 | `mm_scroll_up` | • <code>[scroll, up]</code> | Mm scroll up |
| 254 | `mm_search_incognito` | • <code>[incognito, search]</code><br>• <code>[private, search]</code><br>• <code>[incognito, search]</code> | Mm search incognito |
| 255 | `mm_select_all` | • <code>[all, select]</code><br>• <code>[everything, select]</code> | Mm select all |
| 256 | `mm_show_bookmarks` | • <code>[bookmarks, list]</code><br>• <code>[bookmarks, show]</code><br>• <code>[bookmarks, my]</code> | Mm show bookmarks |
| 257 | `mm_show_desktop` | • <code>[desktop, show]</code> | Mm show desktop |
| 258 | `mm_snip` | • <code>[snip]</code><br>• <code>[snipping, tool]</code><br>• <code>[screenshot, tool]</code><br>• <code>[capture, region]</code> | Mm snip |
| 259 | `mm_space_key` | • <code>[press, space]</code><br>• <code>[spacebar]</code> | Mm space key |
| 260 | `mm_switch_window` | • <code>[switch, window]</code><br>• <code>[next, window]</code> | Mm switch window |
| 261 | `mm_tab_key` | • <code>[press, tab]</code> | Mm tab key |
| 262 | `mm_tab_n` | • <code>[first, tab]</code><br>• <code>[second, tab]</code><br>• <code>[tab, third]</code><br>• <code>[fourth, tab]</code><br>• <code>[fifth, tab]</code><br>• <code>[sixth, tab]</code><br>• <code>[seventh, tab]</code><br>• <code>[eighth, tab]</code><br>• <code>[ninth, tab]</code><br>• <code>[first, page]</code><br>• <code>[page, second]</code><br>• <code>[page, third]</code> | Mm tab n |
| 263 | `mm_tab_next` | • <code>[next, tab]</code><br>• <code>[next, tab]</code> | Mm tab next |
| 264 | `mm_tab_prev` | • <code>[previous, tab]</code><br>• <code>[previous, tab]</code><br>• <code>[prev, tab]</code> | Mm tab prev |
| 265 | `mm_task_view` | • <code>[task, view]</code><br>• <code>[all, windows]</code><br>• <code>[all, view]</code><br>• <code>[all, show, windows]</code> | Mm task view |
| 266 | `mm_type_text` | • <code>[this, type]</code><br>• <code>[text, type]</code> | Mm type text |
| 267 | `mm_undo` | • <code>[that, undo]</code><br>• <code>[undo]</code> | Mm undo |
| 268 | `mm_webcam_photo` | • <code>[photo, webcam]</code><br>• <code>[photo, take]</code> | Mm webcam photo |
| 269 | `mm_yt_video` | • <code>[download, youtube]</code><br>• <code>[download, youtube]</code> | Mm yt video |
| 270 | `vt_type` | • <code>[type]</code><br>• <code>[auto, type]</code> | Vt type |

---

## 💻 Developer, Git, Docker, System & Package Management (110 Executors)

| # | Executor Identifier | Natural Trigger Word Sets | Description / Action |
|---|---|---|---|
| 271 | `cl_apt_clean` | • <code>[apt, clean]</code> | Cl apt clean |
| 272 | `cl_find_duplicates` | • <code>[duplicates]</code> | Cl find duplicates |
| 273 | `cl_find_empty` | • <code>[empty, files]</code> | Cl find empty |
| 274 | `cl_find_hidden` | • <code>[files, hidden]</code> | Cl find hidden |
| 275 | `cl_find_large` | • <code>[files, large]</code><br>• <code>[find, large]</code> | Cl find large |
| 276 | `cl_find_old` | • <code>[find, old]</code><br>• <code>[files, old]</code> | Cl find old |
| 277 | `cl_free_mem` | • <code>[free, memory]</code><br>• <code>[clear, ram]</code> | Cl free mem |
| 278 | `cl_tree` | • <code>[tree]</code> | Cl tree |
| 279 | `dev_apt_install` | • <code>[apt, install]</code> | Dev apt install |
| 280 | `dev_apt_remove` | • <code>[apt, remove]</code> | Dev apt remove |
| 281 | `dev_apt_update` | • <code>[apt, update]</code> | Dev apt update |
| 282 | `dev_b64dec` | • <code>[base64, decode]</code><br>• <code>[base64, decode]</code> | Dev b64dec |
| 283 | `dev_b64enc` | • <code>[base64, encode]</code><br>• <code>[base64, encode]</code> | Dev b64enc |
| 284 | `dev_benchmark` | • <code>[benchmark]</code> | Dev benchmark |
| 285 | `dev_char_code` | • <code>[char, code]</code><br>• <code>[ascii, code]</code><br>• <code>[unicode]</code> | Dev char code |
| 286 | `dev_color_hex` | • <code>[color, hex]</code><br>• <code>[hex, rgb, to]</code><br>• <code>[hex, rgb, to]</code><br>• <code>[color, picker]</code> | Dev color hex |
| 287 | `dev_commit_msg` | • <code>[commit, message]</code><br>• <code>[commit, write]</code> | Dev commit msg |
| 288 | `dev_count_lines` | • <code>[count, lines]</code> | Dev count lines |
| 289 | `dev_coverage` | • <code>[coverage]</code> | Dev coverage |
| 290 | `dev_cron` | • <code>[cron, help]</code><br>• <code>[cron, format]</code> | Dev cron |
| 291 | `dev_csv2json` | • <code>[csv, json, to]</code> | Dev csv2json |
| 292 | `dev_docker_build` | • <code>[build, docker]</code> | Dev docker build |
| 293 | `dev_docker_exec` | • <code>[docker, exec]</code> | Dev docker exec |
| 294 | `dev_docker_help` | • <code>[docker, help]</code> | Dev docker help |
| 295 | `dev_docker_images` | • <code>[docker, images]</code> | Dev docker images |
| 296 | `dev_docker_logs` | • <code>[docker, logs]</code> | Dev docker logs |
| 297 | `dev_docker_prune` | • <code>[docker, prune]</code> | Dev docker prune |
| 298 | `dev_docker_ps` | • <code>[docker, ps]</code> | Dev docker ps |
| 299 | `dev_docker_pull` | • <code>[docker, pull]</code> | Dev docker pull |
| 300 | `dev_docker_rm` | • <code>[docker, rm]</code> | Dev docker rm |
| 301 | `dev_docker_start` | • <code>[docker, start]</code> | Dev docker start |
| 302 | `dev_docker_stats` | • <code>[docker, stats]</code> | Dev docker stats |
| 303 | `dev_docker_stop` | • <code>[docker, stop]</code> | Dev docker stop |
| 304 | `dev_env_vars` | • <code>[env, vars]</code><br>• <code>[environment, variables]</code> | Dev env vars |
| 305 | `dev_find_todos` | • <code>[find, todos]</code> | Dev find todos |
| 306 | `dev_gen_docker` | • <code>[dockerfile, generate]</code> | Dev gen docker |
| 307 | `dev_gen_reqs` | • <code>[generate, requirements]</code> | Dev gen reqs |
| 308 | `dev_git_add` | • <code>[add, git]</code> | Dev git add |
| 309 | `dev_git_amend` | • <code>[amend, git]</code> | Dev git amend |
| 310 | `dev_git_blame` | • <code>[blame, git]</code> | Dev git blame |
| 311 | `dev_git_branch` | • <code>[branch, git]</code> | Dev git branch |
| 312 | `dev_git_branches` | • <code>[branches, git]</code> | Dev git branches |
| 313 | `dev_git_cfg` | • <code>[config, git]</code> | Dev git cfg |
| 314 | `dev_git_checkout` | • <code>[checkout, git]</code> | Dev git checkout |
| 315 | `dev_git_clone` | • <code>[clone, git]</code> | Dev git clone |
| 316 | `dev_git_commit` | • <code>[commit, git]</code> | Dev git commit |
| 317 | `dev_git_diff` | • <code>[diff, git]</code> | Dev git diff |
| 318 | `dev_git_fetch` | • <code>[fetch, git]</code> | Dev git fetch |
| 319 | `dev_git_graph` | • <code>[git, graph]</code> | Dev git graph |
| 320 | `dev_git_help` | • <code>[git, help]</code><br>• <code>[cheat, git]</code> | Dev git help |
| 321 | `dev_git_init` | • <code>[git, init]</code> | Dev git init |
| 322 | `dev_git_log` | • <code>[git, log]</code> | Dev git log |
| 323 | `dev_git_merge` | • <code>[git, merge]</code> | Dev git merge |
| 324 | `dev_git_pull` | • <code>[git, pull]</code> | Dev git pull |
| 325 | `dev_git_push` | • <code>[git, push]</code> | Dev git push |
| 326 | `dev_git_remote` | • <code>[git, remote]</code><br>• <code>[git, remote]</code> | Dev git remote |
| 327 | `dev_git_reset` | • <code>[git, reset]</code> | Dev git reset |
| 328 | `dev_git_show` | • <code>[git, show]</code> | Dev git show |
| 329 | `dev_git_stash` | • <code>[git, stash]</code><br>• <code>[git, stash]</code> | Dev git stash |
| 330 | `dev_git_stash_pop` | • <code>[git, pop, stash]</code> | Dev git stash pop |
| 331 | `dev_git_status` | • <code>[git, status]</code> | Dev git status |
| 332 | `dev_git_tag` | • <code>[git, tag]</code> | Dev git tag |
| 333 | `dev_git_tags` | • <code>[git, tags]</code> | Dev git tags |
| 334 | `dev_git_undo` | • <code>[git, undo]</code> | Dev git undo |
| 335 | `dev_git_whoami` | • <code>[git, whoami]</code> | Dev git whoami |
| 336 | `dev_gitignore` | • <code>[gitignore]</code> | Dev gitignore |
| 337 | `dev_hash` | • <code>[checksum]</code><br>• <code>[file, hash]</code><br>• <code>[file, hash]</code> | Dev hash |
| 338 | `dev_http_serve` | • <code>[http, server]</code><br>• <code>[serve]</code> | Dev http serve |
| 339 | `dev_http_status` | • <code>[http, status]</code><br>• <code>[code, status]</code> | Dev http status |
| 340 | `dev_json2yaml` | • <code>[json, to, yaml]</code> | Dev json2yaml |
| 341 | `dev_json_format` | • <code>[format, json]</code> | Dev json format |
| 342 | `dev_jwt_decode` | • <code>[decode, jwt]</code> | Dev jwt decode |
| 343 | `dev_localhost` | • <code>[localhost]</code> | Dev localhost |
| 344 | `dev_make` | • <code>[make]</code> | Dev make |
| 345 | `dev_markdown` | • <code>[help, markdown]</code><br>• <code>[markdown, syntax]</code> | Dev markdown |
| 346 | `dev_mypy` | • <code>[mypy]</code> | Dev mypy |
| 347 | `dev_new_project` | • <code>[create, project]</code> | Dev new project |
| 348 | `dev_npm_audit` | • <code>[audit, npm]</code> | Dev npm audit |
| 349 | `dev_npm_build` | • <code>[build, npm]</code> | Dev npm build |
| 350 | `dev_npm_install` | • <code>[install, npm]</code> | Dev npm install |
| 351 | `dev_npm_list` | • <code>[list, npm]</code> | Dev npm list |
| 352 | `dev_npm_outdated` | • <code>[npm, outdated]</code> | Dev npm outdated |
| 353 | `dev_npm_run` | • <code>[npm, run]</code> | Dev npm run |
| 354 | `dev_npm_start` | • <code>[npm, start]</code> | Dev npm start |
| 355 | `dev_npm_test` | • <code>[npm, test]</code> | Dev npm test |
| 356 | `dev_open_ports` | • <code>[open, ports]</code><br>• <code>[listening, ports]</code> | Dev open ports |
| 357 | `dev_open_proj` | • <code>[open, project]</code> | Dev open proj |
| 358 | `dev_pip_freeze` | • <code>[freeze, pip]</code> | Dev pip freeze |
| 359 | `dev_pip_install` | • <code>[install, pip]</code> | Dev pip install |
| 360 | `dev_pip_list` | • <code>[list, pip]</code><br>• <code>[list, packages]</code> | Dev pip list |
| 361 | `dev_pip_update` | • <code>[pip, update]</code> | Dev pip update |
| 362 | `dev_port_check` | • <code>[check, port]</code><br>• <code>[check, port]</code> | Dev port check |
| 363 | `dev_profile` | • <code>[profile, python]</code> | Dev profile |
| 364 | `dev_py_format` | • <code>[format, python]</code> | Dev py format |
| 365 | `dev_py_lint` | • <code>[lint]</code> | Dev py lint |
| 366 | `dev_pytest` | • <code>[pytest]</code><br>• <code>[run, tests]</code> | Dev pytest |
| 367 | `dev_regex_cheat` | • <code>[cheat, regex]</code><br>• <code>[help, regex]</code> | Dev regex cheat |
| 368 | `dev_regex_test` | • <code>[regex, test]</code> | Dev regex test |
| 369 | `dev_release_notes` | • <code>[notes, release]</code><br>• <code>[changelog]</code> | Dev release notes |
| 370 | `dev_run_py` | • <code>[python, run]</code> | Dev run py |
| 371 | `dev_run_sh` | • <code>[run, script]</code> | Dev run sh |
| 372 | `dev_show_path` | • <code>[path, show]</code> | Dev show path |
| 373 | `dev_sql_help` | • <code>[help, sql]</code><br>• <code>[cheat, sql]</code> | Dev sql help |
| 374 | `dev_uuid` | • <code>[uuid]</code><br>• <code>[generate, uuid]</code> | Dev uuid |
| 375 | `dev_venv` | • <code>[create, venv]</code> | Dev venv |
| 376 | `dev_ver_git` | • <code>[git, version]</code> | Dev ver git |
| 377 | `dev_ver_node` | • <code>[node, version]</code> | Dev ver node |
| 378 | `dev_ver_py` | • <code>[python, version]</code> | Dev ver py |
| 379 | `dev_which` | • <code>[which]</code> | Dev which |
| 380 | `dev_yaml2json` | • <code>[json, to, yaml]</code> | Dev yaml2json |

---

## 📁 File System & Disk Operations (41 Executors)

| # | Executor Identifier | Natural Trigger Word Sets | Description / Action |
|---|---|---|---|
| 381 | `fs_abspath` | • <code>[absolute, path]</code> | Fs abspath |
| 382 | `fs_append` | • <code>[append]</code> | Fs append |
| 383 | `fs_backup` | • <code>[backup]</code> | Fs backup |
| 384 | `fs_batch_rename` | • <code>[batch, rename]</code> | Fs batch rename |
| 385 | `fs_compare` | • <code>[compare, files]</code> | Fs compare |
| 386 | `fs_count` | • <code>[count, files]</code> | Fs count |
| 387 | `fs_cp_dir` | • <code>[copy, folder]</code> | Fs cp dir |
| 388 | `fs_cp_file` | • <code>[copy, file]</code> | Fs cp file |
| 389 | `fs_decrypt_file` | • <code>[decrypt, file]</code> | Fs decrypt file |
| 390 | `fs_del_dir` | • <code>[delete, folder]</code><br>• <code>[folder, remove]</code> | Fs del dir |
| 391 | `fs_del_file` | • <code>[delete, file]</code><br>• <code>[file, remove]</code> | Fs del file |
| 392 | `fs_du` | • <code>[disk, usage]</code> | Fs du |
| 393 | `fs_encrypt_file` | • <code>[encrypt, file]</code> | Fs encrypt file |
| 394 | `fs_find_symlinks` | • <code>[find, symlinks]</code> | Fs find symlinks |
| 395 | `fs_grep` | • <code>[grep]</code><br>• <code>[search, text]</code><br>• <code>[search, word]</code> | Fs grep |
| 396 | `fs_info` | • <code>[file, info]</code><br>• <code>[details, file]</code> | Fs info |
| 397 | `fs_join` | • <code>[files, join]</code> | Fs join |
| 398 | `fs_ls` | • <code>[files, list]</code><br>• <code>[ls]</code><br>• <code>[dir]</code> | Fs ls |
| 399 | `fs_make_exec` | • <code>[executable, make]</code><br>• <code>[chmod]</code> | Fs make exec |
| 400 | `fs_mime_type` | • <code>[file, type]</code><br>• <code>[mime, type]</code> | Fs mime type |
| 401 | `fs_mkdir` | • <code>[create, folder]</code><br>• <code>[folder, make]</code><br>• <code>[folder, new]</code><br>• <code>[mkdir]</code> | Fs mkdir |
| 402 | `fs_mv_dir` | • <code>[folder, move]</code> | Fs mv dir |
| 403 | `fs_mv_file` | • <code>[file, move]</code> | Fs mv file |
| 404 | `fs_open` | • <code>[file, open]</code> | Fs open |
| 405 | `fs_open_loc` | • <code>[reveal]</code> | Fs open loc |
| 406 | `fs_org_dl` | • <code>[downloads, organize]</code><br>• <code>[downloads, sort]</code> | Fs org dl |
| 407 | `fs_perms` | • <code>[file, permissions]</code> | Fs perms |
| 408 | `fs_read` | • <code>[file, read]</code><br>• <code>[cat]</code> | Fs read |
| 409 | `fs_recent` | • <code>[files, recent]</code> | Fs recent |
| 410 | `fs_rename` | • <code>[rename]</code> | Fs rename |
| 411 | `fs_replace_text` | • <code>[replace, text]</code> | Fs replace text |
| 412 | `fs_search` | • <code>[files, search]</code><br>• <code>[files, find]</code> | Fs search |
| 413 | `fs_size` | • <code>[folder, size]</code> | Fs size |
| 414 | `fs_sort_size` | • <code>[files, size, sort]</code> | Fs sort size |
| 415 | `fs_split` | • <code>[file, split]</code> | Fs split |
| 416 | `fs_symlink` | • <code>[create, symlink]</code> | Fs symlink |
| 417 | `fs_tail` | • <code>[tail]</code> | Fs tail |
| 418 | `fs_touch` | • <code>[create, file]</code><br>• <code>[file, new]</code><br>• <code>[touch]</code> | Fs touch |
| 419 | `fs_unzip` | • <code>[unzip]</code><br>• <code>[extract]</code> | Fs unzip |
| 420 | `fs_watch` | • <code>[file, watch]</code> | Fs watch |
| 421 | `fs_zip` | • <code>[zip]</code><br>• <code>[compress]</code> | Fs zip |

---

## 📅 Productivity, Notes, Reminders, Text Tools & Utilities (152 Executors)

| # | Executor Identifier | Natural Trigger Word Sets | Description / Action |
|---|---|---|---|
| 422 | `p2_add_days` | • <code>[add, days]</code> | P2 add days |
| 423 | `p2_age_calc` | • <code>[how, old]</code><br>• <code>[age, my]</code> | P2 age calc |
| 424 | `p2_biz_days` | • <code>[business, days]</code> | P2 biz days |
| 425 | `p2_charcount` | • <code>[char, count]</code> | P2 charcount |
| 426 | `p2_clip_pwd` | • <code>[directory, working]</code><br>• <code>[current, directory]</code><br>• <code>[pwd]</code> | P2 clip pwd |
| 427 | `p2_clip_read` | • <code>[clipboard, read]</code><br>• <code>[clipboard]</code> | P2 clip read |
| 428 | `p2_date_add` | • <code>[add, weeks]</code><br>• <code>[add, months]</code> | P2 date add |
| 429 | `p2_date_fmt` | • <code>[date, format]</code><br>• <code>[date, format]</code> | P2 date fmt |
| 430 | `p2_days_between` | • <code>[between, days]</code><br>• <code>[date, difference]</code> | P2 days between |
| 431 | `p2_days_left_year` | • <code>[days, left, year]</code> | P2 days left year |
| 432 | `p2_distance` | • <code>[between, distance]</code> | P2 distance |
| 433 | `p2_epoch` | • <code>[epoch]</code><br>• <code>[epoch, time]</code><br>• <code>[timestamp, unix]</code><br>• <code>[time, unix]</code><br>• <code>[timestamp]</code> | P2 epoch |
| 434 | `p2_flight_est` | • <code>[flight, time]</code><br>• <code>[time, travel]</code> | P2 flight est |
| 435 | `p2_leap_year` | • <code>[leap, year]</code> | P2 leap year |
| 436 | `p2_lorem` | • <code>[ipsum, lorem]</code><br>• <code>[ipsum, lorem]</code><br>• <code>[placeholder, text]</code> | P2 lorem |
| 437 | `p2_month_days` | • <code>[days, month]</code> | P2 month days |
| 438 | `p2_moonphase` | • <code>[moon, phase]</code> | P2 moonphase |
| 439 | `p2_next_weekday` | • <code>[monday, next]</code><br>• <code>[friday, next]</code><br>• <code>[next, weekend]</code> | P2 next weekday |
| 440 | `p2_percentage` | • <code>[percentage]</code><br>• <code>[of, percent]</code> | P2 percentage |
| 441 | `p2_qr_code` | • <code>[code, qr]</code><br>• <code>[generate, qr]</code> | P2 qr code |
| 442 | `p2_quarter` | • <code>[quarter]</code><br>• <code>[current, quarter]</code> | P2 quarter |
| 443 | `p2_reading_time` | • <code>[reading, time]</code> | P2 reading time |
| 444 | `p2_stopwatch` | • <code>[stopwatch]</code> | P2 stopwatch |
| 445 | `p2_sunrise` | • <code>[rise, sun]</code><br>• <code>[sunset]</code> | P2 sunrise |
| 446 | `p2_time_diff` | • <code>[difference, time]</code> | P2 time diff |
| 447 | `p2_tz_convert` | • <code>[time, zone]</code><br>• <code>[timezone]</code><br>• <code>[convert, time, zone]</code> | P2 tz convert |
| 448 | `p2_week_num` | • <code>[number, week]</code><br>• <code>[iso, week]</code> | P2 week num |
| 449 | `p2_weeknum` | • <code>[number, week]</code><br>• <code>[current, week]</code><br>• <code>[number, week]</code> | P2 weeknum |
| 450 | `p2_what_day` | • <code>[day, what]</code><br>• <code>[day, of, week]</code> | P2 what day |
| 451 | `p2_wordcount` | • <code>[count, word]</code><br>• <code>[count, words]</code><br>• <code>[stats, text]</code> | P2 wordcount |
| 452 | `p2_world_time` | • <code>[time, world]</code><br>• <code>[in, time]</code> | P2 world time |
| 453 | `p2_worldclock` | • <code>[clock, world]</code><br>• <code>[timezone]</code> | P2 worldclock |
| 454 | `p_alarm` | • <code>[alarm]</code><br>• <code>[alarm, set]</code> | P alarm |
| 455 | `p_boil_eggs` | • <code>[boil, eggs]</code> | P boil eggs |
| 456 | `p_bp` | • <code>[blood, pressure]</code> | P bp |
| 457 | `p_break` | • <code>[break, time]</code><br>• <code>[break, take]</code><br>• <code>[break, timer]</code> | P break |
| 458 | `p_budget` | • <code>[budget]</code> | P budget |
| 459 | `p_calc` | • <code>[calculate]</code><br>• <code>[math]</code> | P calc |
| 460 | `p_calendar` | • <code>[calendar]</code> | P calendar |
| 461 | `p_clip_copy` | • <code>[clipboard, copy, to]</code> | P clip copy |
| 462 | `p_clip_hist` | • <code>[clipboard, history]</code> | P clip hist |
| 463 | `p_clipboard` | • <code>[clipboard]</code><br>• <code>[paste]</code> | P clipboard |
| 464 | `p_convert` | • <code>[convert]</code> | P convert |
| 465 | `p_cook_timer` | • <code>[cooking, timer]</code> | P cook timer |
| 466 | `p_countdown` | • <code>[countdown]</code><br>• <code>[count, down]</code> | P countdown |
| 467 | `p_date` | • <code>[date]</code><br>• <code>[today]</code> | P date |
| 468 | `p_day` | • <code>[day]</code> | P day |
| 469 | `p_days_until` | • <code>[days, until]</code> | P days until |
| 470 | `p_email_draft` | • <code>[draft, email]</code><br>• <code>[email, write]</code><br>• <code>[email, subject]</code> | P email draft |
| 471 | `p_exercise` | • <code>[sit, ups]</code><br>• <code>[push, ups]</code><br>• <code>[workout]</code><br>• <code>[exercise]</code> | P exercise |
| 472 | `p_exp_show` | • <code>[expenses, show]</code> | P exp show |
| 473 | `p_exp_total` | • <code>[expenses, total]</code> | P exp total |
| 474 | `p_expense` | • <code>[add, expense]</code> | P expense |
| 475 | `p_flashcard` | • <code>[cards, flash]</code><br>• <code>[flashcard]</code><br>• <code>[flashcards]</code> | P flashcard |
| 476 | `p_focus` | • <code>[focus, mode]</code><br>• <code>[disturb, do, not]</code><br>• <code>[timer, work]</code> | P focus |
| 477 | `p_goal` | • <code>[goal, set]</code> | P goal |
| 478 | `p_goal_show` | • <code>[goals, show]</code> | P goal show |
| 479 | `p_gratitude` | • <code>[gratitude]</code> | P gratitude |
| 480 | `p_habit` | • <code>[habit, tracker]</code><br>• <code>[habit, track]</code><br>• <code>[habit]</code><br>• <code>[habit, log]</code><br>• <code>[streak]</code> | P habit |
| 481 | `p_habit_add` | • <code>[add, habit]</code> | P habit add |
| 482 | `p_habit_show` | • <code>[habits, show]</code><br>• <code>[habits, my]</code><br>• <code>[habits, my]</code> | P habit show |
| 483 | `p_heart_rate` | • <code>[heart, rate]</code> | P heart rate |
| 484 | `p_journal` | • <code>[journal]</code><br>• <code>[diary]</code> | P journal |
| 485 | `p_journal_read` | • <code>[journal, read]</code> | P journal read |
| 486 | `p_kanban` | • <code>[kanban]</code> | P kanban |
| 487 | `p_linkedin` | • <code>[linkedin, message]</code> | P linkedin |
| 488 | `p_med_reminder` | • <code>[medication, reminder]</code><br>• <code>[medicine, time]</code> | P med reminder |
| 489 | `p_meeting` | • <code>[meeting, notes]</code> | P meeting |
| 490 | `p_mood` | • <code>[log, mood]</code><br>• <code>[mood]</code> | P mood |
| 491 | `p_note_add` | • <code>[add, note]</code> | P note add |
| 492 | `p_note_add_structured` | • <code>[note]</code><br>• <code>[note, quick]</code><br>• <code>[note, sticky]</code> | P note add structured |
| 493 | `p_note_delete` | • <code>[delete, note]</code> | P note delete |
| 494 | `p_note_read` | • <code>[note, read]</code> | P note read |
| 495 | `p_note_search` | • <code>[note, search]</code><br>• <code>[notes, search]</code> | P note search |
| 496 | `p_notes_clear` | • <code>[clear, notes]</code> | P notes clear |
| 497 | `p_notes_list` | • <code>[list, notes]</code><br>• <code>[list, notes]</code> | P notes list |
| 498 | `p_notes_read` | • <code>[notes, show]</code><br>• <code>[my, notes]</code><br>• <code>[note, pad]</code> | P notes read |
| 499 | `p_password` | • <code>[password]</code><br>• <code>[generate, password]</code> | P password |
| 500 | `p_pomodoro` | • <code>[pomodoro]</code><br>• <code>[focus, timer]</code><br>• <code>[sprint]</code> | P pomodoro |
| 501 | `p_quiz` | • <code>[quiz]</code> | P quiz |
| 502 | `p_reading_list` | • <code>[list, reading]</code><br>• <code>[add, read, to]</code><br>• <code>[book, list]</code> | P reading list |
| 503 | `p_remind` | • <code>[remind]</code><br>• <code>[reminder]</code> | P remind |
| 504 | `p_reminders_clear` | • <code>[clear, reminders]</code> | P reminders clear |
| 505 | `p_reminders_show` | • <code>[reminders, show]</code><br>• <code>[my, reminders]</code> | P reminders show |
| 506 | `p_rng` | • <code>[number, random]</code><br>• <code>[between, random]</code> | P rng |
| 507 | `p_savings` | • <code>[goal, savings]</code> | P savings |
| 508 | `p_shopping` | • <code>[list, shopping]</code><br>• <code>[grocery, list]</code><br>• <code>[add, shopping, to]</code> | P shopping |
| 509 | `p_sleep` | • <code>[sleep, tracker]</code><br>• <code>[log, sleep]</code> | P sleep |
| 510 | `p_sms_draft` | • <code>[draft, sms]</code> | P sms draft |
| 511 | `p_split_bill` | • <code>[bill, split]</code><br>• <code>[dutch]</code> | P split bill |
| 512 | `p_standup` | • <code>[stand, up]</code><br>• <code>[daily, standup]</code> | P standup |
| 513 | `p_steps` | • <code>[steps, today]</code><br>• <code>[counter, step]</code> | P steps |
| 514 | `p_time` | • <code>[time]</code><br>• <code>[time, what]</code><br>• <code>[clock]</code> | P time |
| 515 | `p_timer` | • <code>[timer]</code><br>• <code>[set, timer]</code><br>• <code>[countdown]</code> | P timer |
| 516 | `p_todo_add` | • <code>[add, todo]</code><br>• <code>[todo]</code><br>• <code>[task]</code> | P todo add |
| 517 | `p_todo_clear` | • <code>[clear, todos]</code><br>• <code>[clear, todos]</code> | P todo clear |
| 518 | `p_todo_del` | • <code>[delete, todo]</code> | P todo del |
| 519 | `p_todo_done` | • <code>[done, todo]</code><br>• <code>[done, mark]</code> | P todo done |
| 520 | `p_todo_show` | • <code>[show, todos]</code><br>• <code>[list, todo]</code><br>• <code>[my, todos]</code><br>• <code>[my, tasks]</code><br>• <code>[list, task]</code><br>• <code>[my, todos]</code><br>• <code>[my, tasks]</code><br>• <code>[list, task]</code> | P todo show |
| 521 | `p_water` | • <code>[drink, water]</code><br>• <code>[reminder, water]</code> | P water |
| 522 | `tt_acronym` | • <code>[acronym]</code><br>• <code>[abbreviation]</code> | Tt acronym |
| 523 | `tt_anagram` | • <code>[anagram]</code> | Tt anagram |
| 524 | `tt_antonym` | • <code>[antonym]</code> | Tt antonym |
| 525 | `tt_ascii_art` | • <code>[art, ascii]</code> | Tt ascii art |
| 526 | `tt_ascii_table` | • <code>[ascii, table]</code> | Tt ascii table |
| 527 | `tt_bin_text` | • <code>[binary, text]</code> | Tt bin text |
| 528 | `tt_bold_text` | • <code>[bold, text]</code> | Tt bold text |
| 529 | `tt_caesar` | • <code>[caesar, cipher]</code> | Tt caesar |
| 530 | `tt_camel` | • <code>[camel, case]</code> | Tt camel |
| 531 | `tt_center` | • <code>[center, text]</code> | Tt center |
| 532 | `tt_char_freq` | • <code>[char, frequency]</code> | Tt char freq |
| 533 | `tt_count_vowels` | • <code>[count, vowels]</code><br>• <code>[consonants, count]</code> | Tt count vowels |
| 534 | `tt_extract_emails` | • <code>[emails, extract]</code> | Tt extract emails |
| 535 | `tt_extract_nums` | • <code>[extract, numbers]</code> | Tt extract nums |
| 536 | `tt_extract_urls` | • <code>[extract, urls]</code> | Tt extract urls |
| 537 | `tt_grammar` | • <code>[grammar]</code> | Tt grammar |
| 538 | `tt_hex_text` | • <code>[decode, hex]</code><br>• <code>[decode, hex]</code><br>• <code>[from, hex]</code><br>• <code>[hex, text]</code> | Tt hex text |
| 539 | `tt_html_decode` | • <code>[decode, html]</code> | Tt html decode |
| 540 | `tt_html_encode` | • <code>[encode, html]</code> | Tt html encode |
| 541 | `tt_json_minify` | • <code>[json, minify]</code> | Tt json minify |
| 542 | `tt_json_validate` | • <code>[json, validate]</code><br>• <code>[json, validate]</code> | Tt json validate |
| 543 | `tt_lower` | • <code>[lowercase]</code> | Tt lower |
| 544 | `tt_morse` | • <code>[code, morse]</code> | Tt morse |
| 545 | `tt_morse_decode` | • <code>[decode, morse]</code> | Tt morse decode |
| 546 | `tt_nato` | • <code>[alphabet, nato]</code> | Tt nato |
| 547 | `tt_num_lines` | • <code>[lines, number]</code> | Tt num lines |
| 548 | `tt_palindrome` | • <code>[palindrome]</code><br>• <code>[is, palindrome]</code><br>• <code>[check, palindrome]</code> | Tt palindrome |
| 549 | `tt_pig_latin` | • <code>[latin, pig]</code> | Tt pig latin |
| 550 | `tt_prefix_lines` | • <code>[add, prefix]</code> | Tt prefix lines |
| 551 | `tt_reverse` | • <code>[reverse]</code> | Tt reverse |
| 552 | `tt_reverse_text` | • <code>[reverse, text]</code> | Tt reverse text |
| 553 | `tt_reverse_words` | • <code>[reverse, words]</code> | Tt reverse words |
| 554 | `tt_rhyme` | • <code>[rhyme]</code><br>• <code>[rhymes, with]</code><br>• <code>[rhyme, word]</code><br>• <code>[rhyme, words]</code> | Tt rhyme |
| 555 | `tt_rm_spaces` | • <code>[remove, spaces]</code> | Tt rm spaces |
| 556 | `tt_rot13` | • <code>[rot13]</code> | Tt rot13 |
| 557 | `tt_sentence` | • <code>[case, sentence]</code> | Tt sentence |
| 558 | `tt_shortcuts` | • <code>[keyboard, shortcut]</code><br>• <code>[shortcuts]</code><br>• <code>[cheat, sheet]</code><br>• <code>[hotkey]</code> | Tt shortcuts |
| 559 | `tt_slugify` | • <code>[slugify]</code> | Tt slugify |
| 560 | `tt_snake` | • <code>[case, snake]</code> | Tt snake |
| 561 | `tt_sort_lines` | • <code>[lines, sort]</code> | Tt sort lines |
| 562 | `tt_spelling` | • <code>[spelling]</code><br>• <code>[spell]</code> | Tt spelling |
| 563 | `tt_suffix_lines` | • <code>[add, suffix]</code> | Tt suffix lines |
| 564 | `tt_synonym` | • <code>[synonym]</code> | Tt synonym |
| 565 | `tt_text_bin` | • <code>[binary, text, to]</code><br>• <code>[binary, text]</code><br>• <code>[binary, encode]</code><br>• <code>[binary, convert]</code> | Tt text bin |
| 566 | `tt_text_hex` | • <code>[hex, text]</code> | Tt text hex |
| 567 | `tt_title` | • <code>[case, title]</code> | Tt title |
| 568 | `tt_unique_lines` | • <code>[lines, unique]</code><br>• <code>[duplicates, remove]</code> | Tt unique lines |
| 569 | `tt_upper` | • <code>[uppercase]</code> | Tt upper |
| 570 | `tt_url_decode` | • <code>[decode, url]</code><br>• <code>[decode, url]</code> | Tt url decode |
| 571 | `tt_url_encode` | • <code>[encode, url]</code><br>• <code>[encode, url]</code> | Tt url encode |
| 572 | `tt_word_freq` | • <code>[frequency, word]</code><br>• <code>[freq, word]</code> | Tt word freq |
| 573 | `tt_wrap` | • <code>[text, wrap]</code><br>• <code>[word, wrap]</code> | Tt wrap |

---

## 📐 Mathematics, Symbolic Solver & Science (45 Executors)

| # | Executor Identifier | Natural Trigger Word Sets | Description / Action |
|---|---|---|---|
| 574 | `me_base_conv` | • <code>[base, convert]</code> | Me base conv |
| 575 | `me_bmi` | • <code>[bmi]</code><br>• <code>[bmi]</code><br>• <code>[weight]</code> | Me bmi |
| 576 | `me_calories` | • <code>[calories]</code> | Me calories |
| 577 | `me_cbrt` | • <code>[cube, root]</code> | Me cbrt |
| 578 | `me_circle` | • <code>[area, circle]</code><br>• <code>[area, circle]</code> | Me circle |
| 579 | `me_comb` | • <code>[combination]</code> | Me comb |
| 580 | `me_compound` | • <code>[compound, interest]</code> | Me compound |
| 581 | `me_cup_convert` | • <code>[cups, grams, to]</code><br>• <code>[cups, grams, to]</code><br>• <code>[convert, cup]</code><br>• <code>[tablespoon]</code><br>• <code>[teaspoon]</code> | Me cup convert |
| 582 | `me_data_size` | • <code>[data, size]</code> | Me data size |
| 583 | `me_derivative` | • <code>[derivative]</code> | Me derivative |
| 584 | `me_discount` | • <code>[discount]</code><br>• <code>[price, sale]</code> | Me discount |
| 585 | `me_factorial` | • <code>[factorial]</code> | Me factorial |
| 586 | `me_fibonacci` | • <code>[fibonacci]</code> | Me fibonacci |
| 587 | `me_fuel` | • <code>[efficiency, fuel]</code> | Me fuel |
| 588 | `me_gcd_lcm` | • <code>[gcd]</code><br>• <code>[lcm]</code> | Me gcd lcm |
| 589 | `me_golden` | • <code>[golden, ratio]</code> | Me golden |
| 590 | `me_integral` | • <code>[integral]</code> | Me integral |
| 591 | `me_interest` | • <code>[calculator, interest]</code> | Me interest |
| 592 | `me_is_prime` | • <code>[prime]</code><br>• <code>[is, prime]</code> | Me is prime |
| 593 | `me_loan` | • <code>[calculator, loan]</code><br>• <code>[emi]</code><br>• <code>[monthly, payment]</code> | Me loan |
| 594 | `me_log` | • <code>[logarithm]</code> | Me log |
| 595 | `me_matrix` | • <code>[matrix]</code> | Me matrix |
| 596 | `me_mortgage` | • <code>[mortgage]</code> | Me mortgage |
| 597 | `me_pct_change` | • <code>[change, percentage]</code> | Me pct change |
| 598 | `me_pct_of` | • <code>[of, percentage]</code><br>• <code>[percent, what]</code> | Me pct of |
| 599 | `me_perm` | • <code>[permutation]</code> | Me perm |
| 600 | `me_pi` | • <code>[pi]</code> | Me pi |
| 601 | `me_polygon` | • <code>[polygon]</code> | Me polygon |
| 602 | `me_prime_factors` | • <code>[factors, prime]</code> | Me prime factors |
| 603 | `me_prime_list` | • <code>[list, prime]</code> | Me prime list |
| 604 | `me_quadratic` | • <code>[quadratic]</code> | Me quadratic |
| 605 | `me_roman` | • <code>[numeral, roman]</code><br>• <code>[roman]</code> | Me roman |
| 606 | `me_sdt` | • <code>[distance, speed, time]</code> | Me sdt |
| 607 | `me_simplify` | • <code>[simplify]</code> | Me simplify |
| 608 | `me_solve` | • <code>[solve]</code><br>• <code>[equation]</code> | Me solve |
| 609 | `me_sqrt` | • <code>[root, square]</code><br>• <code>[sqrt]</code> | Me sqrt |
| 610 | `me_stats` | • <code>[statistics]</code> | Me stats |
| 611 | `me_tax` | • <code>[tax]</code><br>• <code>[gst]</code><br>• <code>[vat]</code> | Me tax |
| 612 | `me_temp_conv` | • <code>[convert, temperature]</code><br>• <code>[celsius, fahrenheit]</code><br>• <code>[celsius, fahrenheit]</code><br>• <code>[kelvin]</code> | Me temp conv |
| 613 | `me_tip` | • <code>[tip]</code> | Me tip |
| 614 | `me_triangle` | • <code>[area, triangle]</code> | Me triangle |
| 615 | `me_trig` | • <code>[sin]</code><br>• <code>[cos]</code><br>• <code>[tan]</code><br>• <code>[trig]</code> | Me trig |
| 616 | `me_unit_conv` | • <code>[km, miles]</code><br>• <code>[km, miles]</code><br>• <code>[kg, pounds]</code><br>• <code>[kg, pounds]</code><br>• <code>[cm, inches]</code><br>• <code>[cm, inches]</code><br>• <code>[feet, meters]</code><br>• <code>[feet, meters]</code><br>• <code>[gallons, liters]</code><br>• <code>[gallons, liters]</code><br>• <code>[grams, ounces]</code><br>• <code>[grams, ounces]</code><br>• <code>[convert, unit]</code><br>• <code>[convert, units]</code> | Me unit conv |
| 617 | `sci_constant` | • <code>[constant, physics]</code><br>• <code>[planck]</code><br>• <code>[light, of, speed]</code><br>• <code>[gravity]</code><br>• <code>[avogadro]</code> | Sci constant |
| 618 | `sci_element` | • <code>[periodic, table]</code><br>• <code>[element]</code><br>• <code>[atomic, number]</code><br>• <code>[chemical, symbol]</code> | Sci element |

---

## 🖥️ System, Hardware, Network & Security Control (120 Executors)

| # | Executor Identifier | Natural Trigger Word Sets | Description / Action |
|---|---|---|---|
| 619 | `net_bluetooth` | • <code>[bluetooth]</code> | Net bluetooth |
| 620 | `net_devices` | • <code>[connected, devices]</code> | Net devices |
| 621 | `net_dns_lookup` | • <code>[dns, lookup]</code><br>• <code>[nslookup]</code> | Net dns lookup |
| 622 | `net_download` | • <code>[download, file]</code><br>• <code>[download]</code><br>• <code>[download]</code> | Net download |
| 623 | `net_firewall` | • <code>[firewall]</code> | Net firewall |
| 624 | `net_flushdns` | • <code>[dns, flush]</code><br>• <code>[clear, dns]</code> | Net flushdns |
| 625 | `net_headers` | • <code>[headers]</code><br>• <code>[headers, http]</code> | Net headers |
| 626 | `net_mac` | • <code>[address, mac]</code> | Net mac |
| 627 | `net_ping` | • <code>[ping]</code> | Net ping |
| 628 | `net_ping_test` | • <code>[connection, test]</code><br>• <code>[check, internet]</code> | Net ping test |
| 629 | `net_revdns` | • <code>[dns, reverse]</code> | Net revdns |
| 630 | `net_routes` | • <code>[route, table]</code> | Net routes |
| 631 | `net_scan_local` | • <code>[network, scan]</code><br>• <code>[devices, local]</code><br>• <code>[network, scan]</code><br>• <code>[network, scan]</code> | Net scan local |
| 632 | `net_speed` | • <code>[speed, test]</code><br>• <code>[internet, speed]</code><br>• <code>[download, speed]</code><br>• <code>[download, speed]</code><br>• <code>[speed, upload]</code><br>• <code>[bandwidth]</code><br>• <code>[network, speed]</code> | Net speed |
| 633 | `net_ssl_check` | • <code>[check, ssl]</code><br>• <code>[certificate, ssl]</code> | Net ssl check |
| 634 | `net_traceroute` | • <code>[traceroute]</code> | Net traceroute |
| 635 | `net_vpn` | • <code>[status, vpn]</code> | Net vpn |
| 636 | `net_whois` | • <code>[whois]</code> | Net whois |
| 637 | `net_wifi_pass` | • <code>[password, wifi]</code> | Net wifi pass |
| 638 | `net_wifi_settings` | • <code>[settings, wifi]</code> | Net wifi settings |
| 639 | `ni_check` | • <code>[check, internet]</code><br>• <code>[connection, internet]</code><br>• <code>[online]</code><br>• <code>[am, online]</code> | Ni check |
| 640 | `ni_interfaces` | • <code>[interfaces, network]</code> | Ni interfaces |
| 641 | `ni_ip` | • <code>[ip, public]</code><br>• <code>[address, ip]</code><br>• <code>[ip, my]</code><br>• <code>[ip, local]</code> | Ni ip |
| 642 | `ni_wifi` | • <code>[wifi]</code><br>• <code>[name, wifi]</code> | Ni wifi |
| 643 | `se_bcrypt` | • <code>[bcrypt]</code> | Se bcrypt |
| 644 | `se_decrypt` | • <code>[decrypt]</code> | Se decrypt |
| 645 | `se_encrypt` | • <code>[encrypt]</code> | Se encrypt |
| 646 | `se_failed_logins` | • <code>[failed, logins]</code><br>• <code>[attempts, login]</code> | Se failed logins |
| 647 | `se_hash_text` | • <code>[hash]</code> | Se hash text |
| 648 | `se_hmac` | • <code>[hmac]</code> | Se hmac |
| 649 | `se_otp` | • <code>[otp]</code> | Se otp |
| 650 | `se_passphrase` | • <code>[passphrase]</code><br>• <code>[generate, passphrase]</code> | Se passphrase |
| 651 | `se_pw_strength` | • <code>[password, strength]</code><br>• <code>[check, password]</code> | Se pw strength |
| 652 | `se_rand_bytes` | • <code>[bytes, random]</code><br>• <code>[secure, token]</code> | Se rand bytes |
| 653 | `se_xor` | • <code>[xor]</code> | Se xor |
| 654 | `sec_show_ssh` | • <code>[show, ssh]</code><br>• <code>[key, public]</code> | Sec show ssh |
| 655 | `sec_shred` | • <code>[shred]</code><br>• <code>[delete, secure]</code> | Sec shred |
| 656 | `sec_ssh_keygen` | • <code>[generate, ssh]</code><br>• <code>[keygen, ssh]</code> | Sec ssh keygen |
| 657 | `si2_audio` | • <code>[audio, devices]</code> | Si2 audio |
| 658 | `si2_autostart` | • <code>[auto, start]</code><br>• <code>[apps, startup]</code> | Si2 autostart |
| 659 | `si2_cron_list` | • <code>[cron]</code><br>• <code>[crontab]</code> | Si2 cron list |
| 660 | `si2_font_size` | • <code>[font, size]</code> | Si2 font size |
| 661 | `si2_fonts` | • <code>[font, list]</code><br>• <code>[fonts, installed]</code> | Si2 fonts |
| 662 | `si2_gpu` | • <code>[gpu]</code><br>• <code>[card, graphics]</code> | Si2 gpu |
| 663 | `si2_iostat` | • <code>[io, stats]</code> | Si2 iostat |
| 664 | `si2_kernel` | • <code>[kernel]</code> | Si2 kernel |
| 665 | `si2_last_logins` | • <code>[last, logins]</code><br>• <code>[logged, who]</code><br>• <code>[logged, who]</code> | Si2 last logins |
| 666 | `si2_locale` | • <code>[locale]</code> | Si2 locale |
| 667 | `si2_lsblk` | • <code>[block, devices]</code> | Si2 lsblk |
| 668 | `si2_lspci` | • <code>[devices, pci]</code> | Si2 lspci |
| 669 | `si2_lsusb` | • <code>[usb]</code><br>• <code>[devices, usb]</code> | Si2 lsusb |
| 670 | `si2_mounted` | • <code>[mounted]</code> | Si2 mounted |
| 671 | `si2_netstat` | • <code>[netstat]</code> | Si2 netstat |
| 672 | `si2_open_files` | • <code>[files, open]</code> | Si2 open files |
| 673 | `si2_osver` | • <code>[os, version]</code> | Si2 osver |
| 674 | `si2_resolution` | • <code>[resolution, screen]</code> | Si2 resolution |
| 675 | `si2_screen_time` | • <code>[screen, time]</code> | Si2 screen time |
| 676 | `si2_summary` | • <code>[hardware, info]</code> | Si2 summary |
| 677 | `si2_svc_list` | • <code>[services]</code><br>• <code>[running, services]</code> | Si2 svc list |
| 678 | `si2_swap` | • <code>[swap]</code> | Si2 swap |
| 679 | `si2_syslog` | • <code>[syslog]</code><br>• <code>[log, system]</code><br>• <code>[log, system]</code> | Si2 syslog |
| 680 | `si2_temp` | • <code>[cpu, temp]</code> | Si2 temp |
| 681 | `si2_tz` | • <code>[info, timezone]</code><br>• <code>[my, timezone]</code> | Si2 tz |
| 682 | `si2_whoami` | • <code>[whoami]</code><br>• <code>[am, i, who]</code><br>• <code>[am, i, who]</code> | Si2 whoami |
| 683 | `si_battery` | • <code>[battery]</code><br>• <code>[battery]</code><br>• <code>[battery, status]</code> | Si battery |
| 684 | `si_cpu` | • <code>[cpu]</code><br>• <code>[processor]</code><br>• <code>[cpu, info]</code> | Si cpu |
| 685 | `si_dark_mode` | • <code>[dark, mode]</code><br>• <code>[mode, night]</code> | Si dark mode |
| 686 | `si_disk` | • <code>[disk]</code><br>• <code>[disk, space]</code> | Si disk |
| 687 | `si_info` | • <code>[info, system]</code><br>• <code>[sysinfo]</code> | Si info |
| 688 | `si_monitor` | • <code>[monitor, system]</code> | Si monitor |
| 689 | `si_proc_kill` | • <code>[kill, process]</code> | Si proc kill |
| 690 | `si_proc_list` | • <code>[processes]</code><br>• <code>[processes, running]</code><br>• <code>[processes, top]</code><br>• <code>[apps, running]</code><br>• <code>[active, apps]</code> | Si proc list |
| 691 | `si_ram` | • <code>[ram]</code><br>• <code>[memory]</code><br>• <code>[memory, usage]</code><br>• <code>[free, memory]</code> | Si ram |
| 692 | `si_swap` | • <code>[swap, usage]</code> | Si swap |
| 693 | `si_temp` | • <code>[temperature]</code><br>• <code>[cpu, temperature]</code><br>• <code>[fan, speed]</code> | Si temp |
| 694 | `si_uptime` | • <code>[uptime]</code> | Si uptime |
| 695 | `si_wallpaper` | • <code>[wallpaper]</code><br>• <code>[change, wallpaper]</code> | Si wallpaper |
| 696 | `si_zombies` | • <code>[zombie]</code> | Si zombies |
| 697 | `sys_add_startup` | • <code>[add, startup]</code><br>• <code>[add, startup]</code><br>• <code>[enable, startup]</code> | Sys add startup |
| 698 | `sys_bell` | • <code>[bell]</code><br>• <code>[beep]</code> | Sys bell |
| 699 | `sys_br_dn` | • <code>[brightness, down]</code><br>• <code>[brightness, decrease]</code><br>• <code>[brightness, reduce]</code><br>• <code>[brightness, lower]</code><br>• <code>[brightness, dim]</code><br>• <code>[dim, screen]</code> | Sys br dn |
| 700 | `sys_br_set` | • <code>[brightness, set]</code><br>• <code>[brightness, set]</code><br>• <code>[brightness, to]</code> | Sys br set |
| 701 | `sys_br_up` | • <code>[brightness, up]</code><br>• <code>[brightness, increase]</code><br>• <code>[brightness, raise]</code><br>• <code>[brighten, screen]</code> | Sys br up |
| 702 | `sys_bt_off` | • <code>[bluetooth, off, turn]</code><br>• <code>[bluetooth, disable]</code><br>• <code>[bluetooth, off]</code> | Sys bt off |
| 703 | `sys_bt_on` | • <code>[bluetooth, on, turn]</code><br>• <code>[bluetooth, enable]</code><br>• <code>[bluetooth, on]</code> | Sys bt on |
| 704 | `sys_cancel_sd` | • <code>[cancel, shutdown]</code> | Sys cancel sd |
| 705 | `sys_clear_temp` | • <code>[clear, temp]</code><br>• <code>[clean, temp]</code><br>• <code>[cache, clear]</code> | Sys clear temp |
| 706 | `sys_close_window` | • <code>[close, window]</code><br>• <code>[close, this, window]</code> | Sys close window |
| 707 | `sys_empty_bin` | • <code>[bin, empty]</code><br>• <code>[empty, trash]</code> | Sys empty bin |
| 708 | `sys_hostname` | • <code>[hostname]</code><br>• <code>[computer, name]</code> | Sys hostname |
| 709 | `sys_lock` | • <code>[lock]</code><br>• <code>[lock, screen]</code> | Sys lock |
| 710 | `sys_logout` | • <code>[logout]</code><br>• <code>[log, out]</code><br>• <code>[out, sign]</code> | Sys logout |
| 711 | `sys_magnifier` | • <code>[magnifier]</code><br>• <code>[magnify]</code> | Sys magnifier |
| 712 | `sys_mute` | • <code>[mute]</code><br>• <code>[silence]</code> | Sys mute |
| 713 | `sys_night` | • <code>[mode, night]</code><br>• <code>[light, night]</code><br>• <code>[blue, light]</code> | Sys night |
| 714 | `sys_notif_center` | • <code>[center, notification]</code><br>• <code>[action, center]</code> | Sys notif center |
| 715 | `sys_notify` | • <code>[notify]</code><br>• <code>[notification]</code> | Sys notify |
| 716 | `sys_refresh` | • <code>[refresh]</code> | Sys refresh |
| 717 | `sys_remove_startup` | • <code>[remove, startup]</code><br>• <code>[remove, startup]</code><br>• <code>[disable, startup]</code> | Sys remove startup |
| 718 | `sys_restart` | • <code>[restart]</code><br>• <code>[reboot]</code> | Sys restart |
| 719 | `sys_shutdown` | • <code>[shutdown]</code><br>• <code>[down, shut]</code><br>• <code>[off, power]</code> | Sys shutdown |
| 720 | `sys_sleep` | • <code>[sleep]</code><br>• <code>[hibernate]</code><br>• <code>[suspend]</code> | Sys sleep |
| 721 | `sys_snipping` | • <code>[snip]</code><br>• <code>[snipping, tool]</code><br>• <code>[screenshot, tool]</code> | Sys snipping |
| 722 | `sys_ss` | • <code>[screenshot]</code><br>• <code>[capture, screen]</code><br>• <code>[capture, screen]</code> | Sys ss |
| 723 | `sys_task_view` | • <code>[task, view]</code><br>• <code>[all, windows]</code> | Sys task view |
| 724 | `sys_taskmgr` | • <code>[manager, task]</code><br>• <code>[activity, monitor]</code> | Sys taskmgr |
| 725 | `sys_unmute` | • <code>[unmute]</code> | Sys unmute |
| 726 | `sys_vol_dn` | • <code>[down, volume]</code><br>• <code>[quieter]</code><br>• <code>[decrease, volume]</code> | Sys vol dn |
| 727 | `sys_vol_max` | • <code>[max, volume]</code> | Sys vol max |
| 728 | `sys_vol_set` | • <code>[set, volume]</code><br>• <code>[set, volume]</code><br>• <code>[volume]</code><br>• <code>[vol]</code><br>• <code>[adjust, volume]</code><br>• <code>[change, volume]</code><br>• <code>[to, volume]</code> | Sys vol set |
| 729 | `sys_vol_up` | • <code>[up, volume]</code><br>• <code>[louder]</code><br>• <code>[increase, volume]</code> | Sys vol up |
| 730 | `sys_wallpaper` | • <code>[wallpaper]</code><br>• <code>[background]</code> | Sys wallpaper |
| 731 | `sys_wifi_off` | • <code>[off, turn, wifi]</code><br>• <code>[disable, wifi]</code><br>• <code>[off, wifi]</code> | Sys wifi off |
| 732 | `sys_wifi_on` | • <code>[on, turn, wifi]</code><br>• <code>[enable, wifi]</code><br>• <code>[on, wifi]</code> | Sys wifi on |
| 733 | `w2_always_top` | • <code>[always, top]</code> | W2 always top |
| 734 | `w2_fullscreen` | • <code>[fullscreen]</code> | W2 fullscreen |
| 735 | `w2_snap_left` | • <code>[left, snap]</code> | W2 snap left |
| 736 | `w2_snap_right` | • <code>[right, snap]</code> | W2 snap right |
| 737 | `win_max` | • <code>[maximize]</code> | Win max |
| 738 | `win_min_all` | • <code>[all, minimize]</code><br>• <code>[desktop, show]</code> | Win min all |

---

## 🤖 Antigravity AI & Assistant Engine (9 Executors)

| # | Executor Identifier | Natural Trigger Word Sets | Description / Action |
|---|---|---|---|
| 739 | `cfg_agy_model_best` | • <code>[best, model]</code><br>• <code>[best, model, use]</code><br>• <code>[best, model, switch]</code><br>• <code>[best, model, set]</code><br>• <code>[model, pro, use]</code><br>• <code>[model, pro, set]</code><br>• <code>[model, smartest]</code><br>• <code>[model, smartest, use]</code><br>• <code>[highest, model, quality]</code><br>• <code>[deep, model, reasoning]</code><br>• <code>[ai, best]</code> | Cfg agy model best |
| 740 | `cfg_agy_model_better` | • <code>[better, model]</code><br>• <code>[better, model, use]</code><br>• <code>[better, model, switch]</code><br>• <code>[better, model, set]</code><br>• <code>[flash, model, use]</code><br>• <code>[flash, model, set]</code><br>• <code>[balanced, model]</code><br>• <code>[balanced, model, use]</code><br>• <code>[model, standard]</code><br>• <code>[model, normal, use]</code><br>• <code>[ai, better]</code> | Cfg agy model better |
| 741 | `cfg_agy_model_cheapest` | • <code>[cheapest, model]</code><br>• <code>[cheapest, model, use]</code><br>• <code>[cheapest, model, switch]</code><br>• <code>[cheapest, model, set]</code><br>• <code>[flash, lite, use]</code><br>• <code>[flash, lite, switch]</code><br>• <code>[flash, lite, set]</code><br>• <code>[fastest, model]</code><br>• <code>[fastest, model, use]</code><br>• <code>[lightweight, model]</code><br>• <code>[cheap, model, use]</code><br>• <code>[ai, cheapest]</code> | Cfg agy model cheapest |
| 742 | `cfg_agy_model_show` | • <code>[model, show]</code><br>• <code>[ai, model, show]</code><br>• <code>[current, model]</code><br>• <code>[ai, current, model]</code><br>• <code>[model, which]</code><br>• <code>[ai, model, which]</code><br>• <code>[ai, model, what]</code> | Cfg agy model show |
| 743 | `nova_clear` | • <code>[clear, nova]</code> | Nova clear |
| 744 | `nova_install_gemini` | • <code>[gemini, install]</code><br>• <code>[install, nova]</code><br>• <code>[install, nova]</code> | Nova install gemini |
| 745 | `nova_off` | • <code>[disable, nova]</code><br>• <code>[nova, off]</code> | Nova off |
| 746 | `nova_on` | • <code>[enable, nova]</code><br>• <code>[nova, on]</code> | Nova on |
| 747 | `nova_status` | • <code>[nova, status]</code><br>• <code>[info, nova]</code> | Nova status |

---
