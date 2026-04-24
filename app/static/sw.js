self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};
    const title   = data.title || 'JOJ Dakar 2026';
    const options = {
        body:             data.body || '',
        icon:             '/static/images/Dakar_2026_Logo.png',
        badge:            '/static/images/Dakar_2026_Logo.png',
        data:             { url: data.url || '/agenda' },
        vibrate:          [200, 100, 200],
        requireInteraction: true,
        tag:              data.tag || 'joj-notif',
    };
    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    const url = event.notification.data?.url || '/agenda';
    event.waitUntil(clients.matchAll({ type: 'window' }).then(list => {
        for (const client of list) {
            if (client.url.includes(url) && 'focus' in client) return client.focus();
        }
        return clients.openWindow(url);
    }));
});
