import { Component, OnInit } from '@angular/core'
import * as moment from 'moment'

interface RssItem {
  title: string | null;
  lastBuildDate: string | null;
  link: string | null;
  newsList: NewsItem[];
  sources: (string | null)[];
}

interface NewsItem {
  title: string;
  link: string;
  guid: string;
  pubDate: string;
  description: string;
  source: string;
  isFavorite: boolean;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})

export class AppComponent implements OnInit {
  favorites: (string | null)[] = []
  rssItem!: RssItem
  filteredNewsItems: NewsItem[] = []
  uniqueSources: (string | null)[] = []
  selectedSources: (string | null)[] = []
  loaded: boolean = false

  constructor() {
    // Load favourites from local storage if available
    const storedFavorites = localStorage.getItem('favourites');
    if (storedFavorites) {
      this.favorites = JSON.parse(storedFavorites);
    }
  }

  transform(value: string | null): string {
    if (!value) {
      return '';
    }
    return value.replace(/\s/g, '_').toLowerCase();
  }

  sortOptions = [
    { value: 'newest', label: 'Newest' },
    { value: 'oldest', label: 'Oldest' },
    { value: 'title_asc', label: 'Title (A-Z)' },
    { value: 'title_desc', label: 'Title (Z-A)' },
    { value: 'source_asc', label: 'Source (A-Z)' },
    { value: 'source_desc', label: 'Source (Z-A)' }
  ]

  selectedSortOption: string = 'newest'; // Default selected option

  showFavorites: boolean = false

  toggleNewsSource(source: string | null) {
    if (this.selectedSources.includes(source)) {
      this.selectedSources = this.selectedSources.filter(s => s !== source);
    } else {
      this.selectedSources.push(source)
    }

    this.filteredNewsItems = this.selectedSources.length > 0 ? this.rssItem.newsList.filter(article => this.selectedSources.includes(article.source)) : this.rssItem.newsList
  }

  filterFavorites(event: Event) {
    this.showFavorites = (event.target as HTMLInputElement).checked
    if (this.showFavorites) {
      this.filteredNewsItems = this.rssItem.newsList.filter(article => this.favorites.includes(article.guid));
    } else {
      // Reset articles to display all articles
      this.filteredNewsItems = this.rssItem.newsList;
    }
  }

  toggleFavorite(guid: string) {
    if (this.favorites.includes(guid)) {
      this.favorites = this.favorites.filter(favGuid => favGuid !== guid);
    } else {
      this.favorites.push(guid);
    }
    localStorage.setItem('favourites', JSON.stringify(this.favorites));
  }

  filterByDate(event: Event) {
    const selectedDate = (event.target as HTMLInputElement).value
    console.log(selectedDate)
    this.filteredNewsItems = selectedDate ? this.rssItem.newsList.filter(item => moment(item.pubDate, 'ddd, DD MMM YYYY HH:mm:ss [GMT]').format('YYYY-MM-DD') === selectedDate) : this.rssItem.newsList
  }

  sortNews(event: Event) {
    const sortOption = (event.target as HTMLInputElement).value
    if (sortOption) {
      switch (sortOption) {
        case 'newest':
          this.filteredNewsItems.sort((a, b) => new Date(b.pubDate).getTime() - new Date(a.pubDate).getTime());
          break;
        case 'oldest':
          this.filteredNewsItems.sort((a, b) => new Date(a.pubDate).getTime() - new Date(b.pubDate).getTime());
          break;
        case 'title_asc':
          this.filteredNewsItems.sort((a, b) => a.title.localeCompare(b.title));
          break;
        case 'title_desc':
          this.filteredNewsItems.sort((a, b) => b.title.localeCompare(a.title));
          break;
        case 'source_asc':
          this.filteredNewsItems.sort((a, b) => a.source.localeCompare(b.source));
          break;
        case 'source_desc':
          this.filteredNewsItems.sort((a, b) => b.source.localeCompare(a.source));
          break;
      }
    }
  }


  ngOnInit(): void {
    fetch('https://api.journey.skillreactor.io/r/f/rss.xml')
      .then(response => response.text())
      .then(xml => {
        let parser = new DOMParser();
        let xmlDoc = parser.parseFromString(xml, 'text/xml')

        console.log(xmlDoc)

        let titleElement = xmlDoc.querySelector('channel > title')
        let lastBuildDateElement = xmlDoc.querySelector('channel > lastBuildDate')
        let linkElement = xmlDoc.querySelector('channel > link')

        if (titleElement && lastBuildDateElement && linkElement) {
          this.rssItem = {
            title: titleElement.textContent,
            lastBuildDate: lastBuildDateElement.textContent,
            link: linkElement.textContent,
            newsList: [],
            sources: Array.from(xmlDoc.querySelectorAll('item > source')).map(source => source.textContent)
          };

          xmlDoc.querySelectorAll('item').forEach(item => {
            let newsItem: NewsItem = {
              title: item.querySelector('title')?.textContent || '',
              link: item.querySelector('link')?.textContent || '',
              guid: item.querySelector('guid')?.textContent || '',
              pubDate: item.querySelector('pubDate')?.textContent || '',
              description: item.querySelector('description')?.textContent || '',
              source: item.querySelector('source')?.textContent || '',
              isFavorite: false
            }
            this.rssItem.newsList.push(newsItem)
          })

          this.loaded = true

          localStorage.setItem('rssData', JSON.stringify(this.rssItem))
          console.log(this.rssItem)
          this.filteredNewsItems = this.rssItem.newsList
          this.uniqueSources = this.rssItem.sources.filter((source, index, self) => self.indexOf(source) === index)
          console.log(this.uniqueSources)

        }
      })
  }
}
