# Generate SEO landing pages for all Estrie municipalities
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Out = Join-Path $Root "estrie"
$BaseUrl = "https://immobiliermaison.com"
$mrcs = Get-Content (Join-Path $Root "data\mrcs.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$Utf8 = New-Object System.Text.UTF8Encoding $true

$TypeLabels = @{
    "ville" = "Ville"
    "village" = "Municipalit&eacute; de village"
    "canton" = "Municipalit&eacute; de canton"
    "municipalite" = "Municipalit&eacute;"
    "paroisse" = "Municipalit&eacute; de paroisse"
    "arrondissement" = "Arrondissement de Sherbrooke"
}

function Slugify([string]$text) {
    $normalized = $text.Normalize([Text.NormalizationForm]::FormD)
    $sb = New-Object Text.StringBuilder
    foreach ($c in $normalized.ToCharArray()) {
        if ([Globalization.CharUnicodeInfo]::GetUnicodeCategory($c) -ne 'NonSpacingMark') {
            [void]$sb.Append($c)
        }
    }
    $s = ($sb.ToString() -replace '[^a-zA-Z0-9\s-]', '' -replace '\s+', '-' -replace '-+', '-').ToLower().Trim('-')
    return $s
}

function Get-EntrySlug($m, $type) {
    if ($m.slug) { return $m.slug }
    return Slugify $m.name
}

$entries = @()
foreach ($mrc in $mrcs) {
    foreach ($m in $mrc.municipalities) {
        $slug = Get-EntrySlug $m $m.type
        $entries += [PSCustomObject]@{
            name = $m.name; type = $m.type; slug = $slug
            mrc_name = $mrc.name; mrc_slug = $mrc.slug; is_borough = $false
        }
    }
    if ($mrc.boroughs) {
        foreach ($b in $mrc.boroughs) {
            $slug = if ($b.slug) { $b.slug } else { Slugify $b.name }
            $entries += [PSCustomObject]@{
                name = $b.name; type = $b.type; slug = $slug
                mrc_name = $mrc.name; mrc_slug = $mrc.slug; is_borough = $true
            }
        }
    }
}

function Fr([string]$t) {
    if (-not $t) { return $t }
    return $t.Replace('é','&eacute;').Replace('É','&Eacute;').Replace('è','&egrave;').Replace('ê','&ecirc;')
        .Replace('à','&agrave;').Replace('ô','&ocirc;').Replace('û','&ucirc;').Replace('ï','&iuml;')
        .Replace('·','&middot;').Replace('ö','&ouml;')
}

function Get-Intro($e) {
    $name = $e.name; $mrc = $e.mrc_name
    if ($e.is_borough) {
        return "Vous souhaitez vendre ou acheter une propri&eacute;t&eacute; de prestige dans l'arrondissement $name &agrave; Sherbrooke ? L'&Eacute;quipe Chiasson de Francesco, courtiers immobiliers RE/MAX D'ABORD, conna&icirc;t intimement le march&eacute; immobilier de ce secteur sherbrookois. De la mise en march&eacute; haut de gamme &agrave; la n&eacute;gociation strat&eacute;gique, nous maximisons la valeur de votre patrimoine dans l'un des arrondissements les plus recherch&eacute;s de l'Estrie."
    }
    if ($e.type -eq 'ville') {
        return "Le march&eacute; immobilier &agrave; $name exige une expertise locale et une mise en march&eacute; irr&eacute;prochable. Bas&eacute;s &agrave; Sherbrooke et actifs dans toute la MRC $mrc, les courtiers de l'&Eacute;quipe Chiasson de Francesco accompagnent vendeurs et acheteurs de propri&eacute;t&eacute;s r&eacute;sidentielles et commerciales &agrave; $name avec rigueur, transparence et un service de prestige."
    }
    return "Que vous poss&eacute;diez une r&eacute;sidence, un chalet ou un terrain &agrave; $name, la vente d'une propri&eacute;t&eacute; en Estrie demande un courtier qui comprend les r&eacute;alit&eacute;s du march&eacute; de la MRC $mrc. L'&Eacute;quipe Chiasson de Francesco offre une &eacute;valuation immobili&egrave;re gratuite, une strat&eacute;gie de mise en march&eacute; sur mesure et un accompagnement personnalis&eacute; pour chaque transaction &agrave; $name."
}

function Get-Market($e) {
    $name = $e.name; $mrc = $e.mrc_name
    $loc = if ($e.is_borough) { "$name, Sherbrooke" } else { $name }
    $tlMap = @{
        "ville" = "ville"
        "village" = "municipalit&eacute; de village"
        "canton" = "municipalit&eacute; de canton"
        "municipalite" = "municipalit&eacute;"
        "paroisse" = "municipalit&eacute; de paroisse"
        "arrondissement" = "arrondissement de Sherbrooke"
    }
    $tl = if ($tlMap.ContainsKey($e.type)) { $tlMap[$e.type] } else { "municipalit&eacute;" }
    return "En tant que $tl de la MRC $mrc, $loc fait partie du dynamisme immobilier de l'Estrie. Notre &eacute;quipe ma&icirc;trise les tendances du march&eacute; local - prix, d&eacute;lais de vente, profil des acheteurs - pour positionner votre propri&eacute;t&eacute; au bon prix et attirer les bonnes offres. Appuy&eacute;s par le r&eacute;seau mondial RE/MAX, nous offrons une visibilit&eacute; exceptionnelle &agrave; chaque inscription."
}

function Render-MuniPage($e) {
    $name = $e.name; $slug = $e.slug; $mrc = $e.mrc_name; $mrcSlug = $e.mrc_slug
    $typLabelRaw = $TypeLabels[$e.type]
    if ($e.is_borough) {
        $title = "Courtier immobilier $name Sherbrooke | Immobilier Estrie - immobiliermaison.com"
        $h1 = "Courtier immobilier - $name, Sherbrooke"
        $geo = "$name, Sherbrooke"
        $bcName = "Sherbrooke"; $bcUrl = "$BaseUrl/estrie/sherbrooke/"
    } else {
        $title = "Courtier immobilier $name | Vendre sa maison en Estrie - immobiliermaison.com"
        $h1 = "Courtier immobilier &agrave; $name"
        $geo = $name
        $bcName = $mrc; $bcUrl = "$BaseUrl/estrie/mrc-$mrcSlug/"
    }
    $canonical = "$BaseUrl/estrie/$slug/"
    $desc = "Courtiers immobiliers RE/MAX &agrave; $geo, Estrie. &Eacute;quipe Chiasson de Francesco - &eacute;valuation gratuite, vente et achat de propri&eacute;t&eacute;s de prestige. MRC $mrc. Appelez (819) 919-4631."
    $intro = Get-Intro $e
    $market = Get-Market $e
    $typLabel = $TypeLabels[$e.type]
    $neighbors = $entries | Where-Object { $_.mrc_slug -eq $mrcSlug -and $_.slug -ne $slug } | Select-Object -First 4
    $neighborHtml = ($neighbors | ForEach-Object {
        "                    <a href=`"$BaseUrl/estrie/$($_.slug)/`" class=`"text-sm text-gray-500 hover:text-remaxRed transition-colors`">$($_.name)</a>"
    }) -join "`n"
    $h2Geo = "Immobilier de prestige &agrave; $geo"
    $bodyCopy = "Pierre-Olivier Chiasson et Marco De Francesco, courtiers immobiliers RE/MAX D'ABORD, vous accompagnent &agrave; chaque &eacute;tape : &eacute;valuation priv&eacute;e gratuite, photographie professionnelle, marketing num&eacute;rique cibl&eacute;, qualification des acheteurs et n&eacute;gociation jusqu'&agrave; l'acte notari&eacute;."
    $li1 = "&Eacute;valuation immobili&egrave;re gratuite et confidentielle"
    $li2 = "Mise en march&eacute; haut de gamme (photo, vid&eacute;o, drone)"
    $li3 = "R&eacute;seau RE/MAX - visibilit&eacute; locale et internationale"
    $li4 = "Avis Google 5 &eacute;toiles"
    $h2Form = "&Eacute;valuation priv&eacute;e - $name"
    $formSub = "Analyse confidentielle de la valeur de votre propri&eacute;t&eacute; &agrave; $geo."
    $h2Near = "Autres municipalit&eacute;s - MRC $mrc"
    $linkAll = "Voir toutes les municipalit&eacute;s de l'Estrie"
    $navMuni = "Municipalit&eacute;s"
    $footTeam = "&Eacute;quipe Chiasson de Francesco &middot; RE/MAX D'ABORD"
    $ogTitle = "Courtier immobilier $name | &Eacute;quipe Chiasson de Francesco"
    $schemaName = "&Eacute;quipe Chiasson de Francesco - $name"

    @"
<!DOCTYPE html>
<html lang="fr-CA" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title</title>
    <meta name="description" content="$desc">
    <meta name="robots" content="index, follow">
    <meta name="geo.region" content="CA-QC">
    <meta name="geo.placename" content="$geo">
    <link rel="canonical" href="$canonical">
    <meta property="og:type" content="website">
    <meta property="og:url" content="$canonical">
    <meta property="og:title" content="$ogTitle">
    <meta property="og:description" content="$desc">
    <meta property="og:locale" content="fr_CA">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config={theme:{extend:{colors:{remaxRed:'#E11B22',luxuryDark:'#0A1128',luxuryLight:'#FDFDFD'},fontFamily:{sans:['Montserrat','sans-serif'],serif:['Playfair Display','serif']},boxShadow:{floating:'0 20px 40px -10px rgba(0,0,0,0.08)'}}}}</script>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
    <script type="application/ld+json">
    {"@context":"https://schema.org","@graph":[
        {"@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Accueil","item":"$BaseUrl/"},
            {"@type":"ListItem","position":2,"name":"Estrie","item":"$BaseUrl/estrie/"},
            {"@type":"ListItem","position":3,"name":"$bcName","item":"$bcUrl"},
            {"@type":"ListItem","position":4,"name":"$name","item":"$canonical"}
        ]},
        {"@type":"RealEstateAgent","name":"$schemaName","url":"$canonical","telephone":"+1-819-919-4631","email":"info@immobiliermaison.com","areaServed":{"@type":"City","name":"$geo"},"parentOrganization":{"@type":"Organization","name":"RE/MAX D'ABORD"}}
    ]}
    </script>
    <style>.form-iframe-wrapper{min-height:624px;border-radius:8px;overflow:hidden;background:#fff}.form-iframe-wrapper iframe{display:block;width:100%;min-height:624px;border:none;border-radius:8px}</style>
</head>
<body class="font-sans text-gray-800 bg-luxuryLight antialiased">
    <header class="fixed w-full top-0 z-50 bg-white/90 backdrop-blur-lg border-b border-gray-100 py-4">
        <div class="max-w-7xl mx-auto px-6 lg:px-12 flex justify-between items-center">
            <a href="$BaseUrl/" class="font-serif text-2xl font-bold text-luxuryDark uppercase">Immobilier<span class="text-remaxRed">maison</span></a>
            <nav class="hidden md:flex items-center gap-8 text-xs font-semibold uppercase tracking-widest text-gray-500">
                <a href="$BaseUrl/estrie/" class="hover:text-luxuryDark">Estrie</a>
                <a href="$BaseUrl/estrie/municipalites/" class="hover:text-luxuryDark">$navMuni</a>
                <a href="tel:+18199194631" class="border border-luxuryDark/20 px-5 py-2 hover:bg-luxuryDark hover:text-white transition">(819) 919-4631</a>
            </nav>
        </div>
    </header>
    <main class="pt-24">
        <section class="bg-luxuryDark text-white py-20">
            <div class="max-w-7xl mx-auto px-6 lg:px-12">
                <nav class="text-xs uppercase tracking-widest text-gray-400 mb-6">
                    <a href="$BaseUrl/" class="hover:text-white">Accueil</a> / <a href="$BaseUrl/estrie/" class="hover:text-white">Estrie</a> / <a href="$bcUrl" class="hover:text-white">$bcName</a> / <span class="text-white">$name</span>
                </nav>
                <p class="text-remaxRed text-xs font-bold uppercase tracking-widest mb-4">$typLabel &middot; MRC $mrc &middot; Estrie</p>
                <h1 class="font-serif text-4xl md:text-6xl leading-tight mb-6">$h1</h1>
                <p class="text-gray-300 font-light text-lg max-w-3xl leading-relaxed">$intro</p>
            </div>
        </section>
        <section class="py-20">
            <div class="max-w-7xl mx-auto px-6 lg:px-12 grid lg:grid-cols-2 gap-16 items-start">
                <div>
                    <h2 class="font-serif text-3xl text-luxuryDark mb-6">$h2Geo</h2>
                    <p class="text-gray-500 font-light leading-relaxed mb-6">$market</p>
                    <p class="text-gray-500 font-light leading-relaxed mb-8">$bodyCopy</p>
                    <ul class="space-y-3 text-sm text-gray-600">
                        <li class="flex gap-3"><span class="text-remaxRed">&#10003;</span> $li1</li>
                        <li class="flex gap-3"><span class="text-remaxRed">&#10003;</span> $li2</li>
                        <li class="flex gap-3"><span class="text-remaxRed">&#10003;</span> $li3</li>
                        <li class="flex gap-3"><span class="text-remaxRed">&#10003;</span> $li4</li>
                    </ul>
                </div>
                <div id="contact" class="bg-white p-6 shadow-floating border border-gray-100">
                    <h2 class="font-serif text-2xl text-luxuryDark mb-2">$h2Form</h2>
                    <p class="text-sm text-gray-500 mb-4 font-light">$formSub</p>
                    <div class="form-iframe-wrapper">
                        <iframe src="https://api.leadconnectorhq.com/widget/form/fZigX6fPzGLkOM4sNUWJ" style="width:100%;height:100%;border:none;border-radius:8px" id="inline-fZigX6fPzGLkOM4sNUWJ" data-form-name="immobiliermaison" data-height="624" title="Formulaire immobiliermaison - $name"></iframe>
                    </div>
                </div>
            </div>
        </section>
        <section class="py-16 bg-white border-y border-gray-100">
            <div class="max-w-7xl mx-auto px-6 lg:px-12">
                <h2 class="font-serif text-2xl text-luxuryDark mb-6">$h2Near</h2>
                <div class="flex flex-wrap gap-4">$neighborHtml</div>
                <p class="mt-8 text-sm text-gray-400"><a href="$BaseUrl/estrie/municipalites/" class="text-remaxRed hover:underline">$linkAll</a></p>
            </div>
        </section>
    </main>
    <footer class="bg-luxuryDark text-white py-12 border-t-4 border-remaxRed">
        <div class="max-w-7xl mx-auto px-6 lg:px-12 flex flex-col md:flex-row justify-between gap-8 text-sm text-gray-400 font-light">
            <div><p class="font-serif text-xl text-white mb-2">Immobilier<span class="text-remaxRed">maison</span></p><p>$footTeam</p></div>
            <div><p><a href="tel:+18199194631" class="hover:text-white">(819) 919-4631</a></p><p><a href="mailto:info@immobiliermaison.com" class="hover:text-white">info@immobiliermaison.com</a></p></div>
            <div><p><a href="$BaseUrl/" class="hover:text-white">Accueil</a></p><p><a href="$BaseUrl/estrie/" class="hover:text-white">Immobilier Estrie</a></p></div>
        </div>
    </footer>
    <script src="https://link.msgsndr.com/js/form_embed.js"></script>
</body>
</html>
"@
}

# Clean output
if (Test-Path $Out) { Remove-Item $Out -Recurse -Force }
New-Item -ItemType Directory -Path $Out -Force | Out-Null

foreach ($e in $entries) {
    $dir = Join-Path $Out $e.slug
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    [IO.File]::WriteAllText((Join-Path $dir "index.html"), (Render-MuniPage $e), $Utf8)
}

# MRC hubs
foreach ($mrc in $mrcs) {
    $muniEntries = $entries | Where-Object { $_.mrc_slug -eq $mrc.slug } | Sort-Object name
    $links = ($muniEntries | ForEach-Object {
        $tl = $TypeLabels[$_.type]
        "                <a href=`"$BaseUrl/estrie/$($_.slug)/`" class=`"p-4 border border-gray-100 hover:border-remaxRed/30 hover:shadow-floating transition block`"><span class=`"font-serif text-lg text-luxuryDark`">$($_.name)</span><span class=`"block text-xs text-gray-400 mt-1`">$tl</span></a>"
    }) -join "`n"
    $dir = Join-Path $Out "mrc-$($mrc.slug)"
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    $html = @"
<!DOCTYPE html>
<html lang="fr-CA">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Courtier immobilier MRC $($mrc.name) | Estrie - immobiliermaison.com</title>
    <meta name="description" content="Courtiers immobiliers RE/MAX dans la MRC $($mrc.name), Estrie. $($muniEntries.Count) municipalites desservies par l'Equipe Chiasson de Francesco.">
    <link rel="canonical" href="$BaseUrl/estrie/mrc-$($mrc.slug)/">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config={theme:{extend:{colors:{remaxRed:'#E11B22',luxuryDark:'#0A1128'},fontFamily:{serif:['Playfair Display','serif'],sans:['Montserrat','sans-serif']}}}}</script>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body class="font-sans bg-[#FDFDFD]">
    <header class="bg-luxuryDark text-white py-6"><div class="max-w-7xl mx-auto px-6"><a href="$BaseUrl/" class="font-serif text-2xl font-bold uppercase">Immobilier<span class="text-remaxRed">maison</span></a></div></header>
    <main class="max-w-7xl mx-auto px-6 py-16">
        <nav class="text-sm text-gray-400 mb-6"><a href="$BaseUrl/estrie/">Estrie</a> / MRC $($mrc.name)</nav>
        <h1 class="font-serif text-4xl md:text-5xl text-luxuryDark mb-6">Courtier immobilier - MRC $($mrc.name)</h1>
        <p class="text-gray-500 font-light text-lg max-w-3xl mb-12">L'Equipe Chiasson de Francesco dessert l'ensemble de la MRC $($mrc.name) en Estrie. Chef-lieu : $($mrc.chef_lieu).</p>
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">$links</div>
    </main>
</body>
</html>
"@
    [IO.File]::WriteAllText((Join-Path $dir "index.html"), $html, $Utf8)
}

# Estrie hub
$mrcSections = ($mrcs | ForEach-Object {
    $m = $_
    $list = ($entries | Where-Object { $_.mrc_slug -eq $m.slug } | Sort-Object name | ForEach-Object {
        "<li><a href=`"$BaseUrl/estrie/$($_.slug)/`" class=`"hover:text-remaxRed`">$($_.name)</a></li>"
    }) -join "`n            "
    @"
        <section class="mb-12">
            <h2 class="font-serif text-2xl text-luxuryDark mb-2"><a href="$BaseUrl/estrie/mrc-$($m.slug)/" class="hover:text-remaxRed">MRC $($m.name)</a></h2>
            <p class="text-sm text-gray-400 mb-4">Chef-lieu : $($m.chef_lieu)</p>
            <ul class="grid sm:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-2 text-sm text-gray-600">$list</ul>
        </section>
"@
}) -join "`n"

$estrieHtml = @"
<!DOCTYPE html>
<html lang="fr-CA">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Courtier immobilier Estrie | Cantons-de-l'Est - immobiliermaison.com</title>
    <meta name="description" content="Courtiers immobiliers RE/MAX dans toute l'Estrie. $($entries.Count) municipalites desservies. Equipe Chiasson de Francesco.">
    <link rel="canonical" href="$BaseUrl/estrie/">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>tailwind.config={theme:{extend:{colors:{remaxRed:'#E11B22',luxuryDark:'#0A1128'},fontFamily:{serif:['Playfair Display','serif'],sans:['Montserrat','sans-serif']}}}}</script>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body class="font-sans bg-[#FDFDFD]">
    <header class="bg-luxuryDark text-white py-8"><div class="max-w-7xl mx-auto px-6"><a href="$BaseUrl/" class="font-serif text-3xl font-bold uppercase">Immobilier<span class="text-remaxRed">maison</span></a></div></header>
    <main class="max-w-7xl mx-auto px-6 py-16">
        <h1 class="font-serif text-4xl md:text-6xl text-luxuryDark mb-6">Courtier immobilier en Estrie</h1>
        <p class="text-gray-500 font-light text-lg max-w-3xl mb-12">L'Estrie compte 9 MRC et $($entries.Count) municipalites. L'Equipe Chiasson de Francesco dessert l'ensemble du territoire.</p>
        <p class="mb-12"><a href="$BaseUrl/estrie/municipalites/" class="text-remaxRed font-semibold text-sm uppercase tracking-widest">Index alphabetique complet</a></p>
        $mrcSections
    </main>
</body>
</html>
"@
[IO.File]::WriteAllText((Join-Path $Out "index.html"), $estrieHtml, $Utf8)

# Municipalities index
$alphaLinks = ($entries | Sort-Object { $_.name.ToLower() } | ForEach-Object {
    "<li><a href=`"$BaseUrl/estrie/$($_.slug)/`" class=`"hover:text-remaxRed`">$($_.name)</a> <span class=`"text-gray-400 text-xs`">($($_.mrc_name))</span></li>"
}) -join "`n"
$muniDir = Join-Path $Out "municipalites"
New-Item -ItemType Directory -Path $muniDir -Force | Out-Null
$muniIndex = @"
<!DOCTYPE html>
<html lang="fr-CA">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toutes les municipalites de l'Estrie | immobiliermaison.com</title>
    <meta name="description" content="Index de $($entries.Count) pages - courtier immobilier par municipalite en Estrie.">
    <link rel="canonical" href="$BaseUrl/estrie/municipalites/">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="font-sans bg-[#FDFDFD] p-8">
    <h1 class="text-3xl font-bold mb-8"><a href="$BaseUrl/estrie/" class="text-gray-400 text-sm">Estrie</a> - Municipalites ($($entries.Count))</h1>
    <ul class="grid sm:grid-cols-2 lg:grid-cols-3 gap-2 text-sm">$alphaLinks</ul>
</body>
</html>
"@
[IO.File]::WriteAllText((Join-Path $muniDir "index.html"), $muniIndex, $Utf8)

# Sitemap
$urls = @("<url><loc>$BaseUrl/</loc><priority>1.0</priority></url>", "<url><loc>$BaseUrl/estrie/</loc><priority>0.9</priority></url>", "<url><loc>$BaseUrl/estrie/municipalites/</loc><priority>0.8</priority></url>")
foreach ($mrc in $mrcs) { $urls += "<url><loc>$BaseUrl/estrie/mrc-$($mrc.slug)/</loc><priority>0.7</priority></url>" }
foreach ($e in $entries) { $urls += "<url><loc>$BaseUrl/estrie/$($e.slug)/</loc><priority>0.6</priority></url>" }
$sitemap = "<?xml version=`"1.0`" encoding=`"UTF-8`"?>`n<urlset xmlns=`"http://www.sitemaps.org/schemas/sitemap/0.9`">`n  $($urls -join "`n  ")`n</urlset>`n"
[IO.File]::WriteAllText((Join-Path $Root "sitemap.xml"), $sitemap, $Utf8)

Write-Host "Generated $($entries.Count) municipality pages + $($mrcs.Count) MRC hubs + 2 index pages"
Write-Host "Sitemap: $($urls.Count) URLs"
