<template>
    <div class="container mt-5">
        <div class="card shadow p-4">
            <h1 class="text-center mb-4">🔗 URL Shortener</h1>

            <div class="input-group mb-3">
                <input type="text" v-model="urlToShorten" class="form-control"
                    placeholder="Paste your long link here..." @keyup.enter="shortenUrl">
                <button class="btn btn-primary" @click="shortenUrl">Shorten</button>
            </div>

            <div v-if="resultUrl" class="alert alert-success">
                Success! Your link: <a :href="resultUrl" target="_blank">{{ resultUrl }}</a>
                <br>
                <small class="text-muted">Code: {{ shortCode }}</small>
            </div>

            <hr class="my-4">

            <h3>📊 Analytics (Redis)</h3>
            <div class="input-group mb-3">
                <input type="text" v-model="codeToCheck" class="form-control"
                    placeholder="Enter short code (e.g., XyZ123)" @keyup.enter="checkStats">
                <button class="btn btn-secondary" @click="checkStats">Check Clicks</button>
            </div>

            <div v-if="stats" class="alert alert-info">
                <p><strong>Original URL:</strong> {{ stats.original_url }}</p>
                <p><strong>Total Clicks:</strong> {{ stats.clicks }}</p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            urlToShorten: '',
            resultUrl: '',
            shortCode: '',
            codeToCheck: '',
            stats: null,
            // VITE_BACKEND_URL берется из переменных окружения
            // Если переменной нет, по умолчанию будет localhost (для локальных тестов)
            backendUrl: import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000'
        }
    },
    methods: {
        async shortenUrl() {
            if (!this.urlToShorten) return;
            try {
                // Убираем слеш в конце URL, если он есть, чтобы не было двойных слешей //
                const baseUrl = this.backendUrl.replace(/\/$/, '');

                const response = await fetch(`${baseUrl}/shorten`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: this.urlToShorten })
                });

                if (!response.ok) throw new Error('Network response was not ok');

                const data = await response.json();
                // Заменяем локальный адрес бэкенда на адрес фронтенда или используем то, что прислал бэк
                this.resultUrl = data.full_short_url.replace('http://localhost:5000', baseUrl);
                this.shortCode = data.short_code;
            } catch (e) {
                alert('Error connecting to the server');
                console.error(e);
            }
        },
        async checkStats() {
            if (!this.codeToCheck) return;
            try {
                const baseUrl = this.backendUrl.replace(/\/$/, '');
                const response = await fetch(`${baseUrl}/stats/${this.codeToCheck}`);

                if (response.ok) {
                    this.stats = await response.json();
                } else {
                    alert('Link not found');
                    this.stats = null;
                }
            } catch (e) {
                alert('Error fetching statistics');
            }
        }
    }
}
</script>

<style>
/* Optional: Make it look nice on mobile */
body {
    background-color: #f8f9fa;
}

.card {
    max-width: 600px;
    margin: 0 auto;
}
</style>