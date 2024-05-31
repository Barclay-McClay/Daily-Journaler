fetch('./blog-posts/blog-data.json')
  .then(response => response.json())
  .then(data => {
    const container = document.querySelector('.grid-container');
    
    data.posts.sort((a, b) => new Date(b.date) - new Date(a.date)); // Sort by date
    
    data.posts.forEach(post => {
      let item = document.createElement('div');
      item.className = 'grid-item';
      
      let title = document.createElement('h2');
      title.innerText = post.title;

      let date = document.createElement('p');
      date.innerText = post.date;

      let image = document.createElement('img');
      image.src = `./blog-posts/blog-images/${post.image}`;

      let preview = document.createElement('p');
      preview.innerText = post.preview;

      let readMore = document.createElement('a');
      readMore.href = post.url;
      readMore.innerText = 'Read More';

      item.append(image, title, date, preview, readMore);
      container.appendChild(item);
    });
  });