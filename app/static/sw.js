self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};
    const title   = data.title || 'JOJ Dakar 2026';
    const options = {
        body:             data.body || '',
        icon:             '/static/images/joj1.jpg',
        badge:            '/static/images/joj1.jpg',
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
