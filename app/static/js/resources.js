document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/articles')
        .then(response => response.json())
        .then(articles => {
            const articlesContainer = document.getElementById('articles-container');
            articlesContainer.innerHTML = ''; // Clear existing content

            if (articles.length === 0) {
                articlesContainer.textContent = 'No articles found.';
            } else {
                articles.forEach(article => {
                    const articleElement = document.createElement('div');
                    articleElement.className = 'article';

                    const imageElement = document.createElement('img');
                    imageElement.src = article.imageUrl;
                    imageElement.alt = article.title;

                    const titleElement = document.createElement('h3');
                    titleElement.textContent = article.title;

                    const descriptionElement = document.createElement('p');
                    descriptionElement.textContent = article.content ? article.content.substring(0, 100) + '...' : 'No description available.';

                    const linkElement = document.createElement('a');
                    linkElement.href = article.url;
                    linkElement.textContent = 'Read more';
                    linkElement.target = '_blank';

                    articleElement.appendChild(imageElement);
                    articleElement.appendChild(titleElement);
                    articleElement.appendChild(descriptionElement);
                    articleElement.appendChild(linkElement);

                    articlesContainer.appendChild(articleElement);
                });
            }
        })
        .catch(error => {
            console.error('Error fetching articles:', error);
            document.getElementById('articles-container').textContent = 'Failed to load articles.';
        });
});
