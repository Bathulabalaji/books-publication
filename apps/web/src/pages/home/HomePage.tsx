import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <div className="site-shell">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>

      <header className="site-header">
        <Link aria-label="PUSTORA home" className="brand" to="/">
          <span aria-hidden="true" className="brand__mark">
            p
          </span>
          <span>pustora</span>
        </Link>

        <nav aria-label="Main navigation" className="site-nav">
          <a href="#our-story">Our story</a>
          <a href="#discover">Discover</a>
        </nav>

        <span className="header-note">A world between the covers</span>
      </header>

      <main id="main-content">
        <section aria-labelledby="hero-title" className="hero">
          <div className="hero__copy">
            <p className="eyebrow">
              <span aria-hidden="true" className="eyebrow__dot" />
              The PUSTORA reading room
            </p>
            <h1 aria-label="Find a little more wonder." id="hero-title">
              Find a little
              <br />
              <span>more wonder.</span>
            </h1>
            <p className="hero__description">
              Thoughtful books for curious minds, quiet moments, and every new chapter in between.
            </p>
            <a className="button button--primary" href="#discover">
              Explore PUSTORA
              <span aria-hidden="true">↗</span>
            </a>
            <p className="hero__aside">Made for the pages you’ll return to.</p>
          </div>

          <div aria-label="An illustrated stack of books" className="hero-art" role="img">
            <div className="hero-art__sun" />
            <div className="hero-art__spark hero-art__spark--one">✳</div>
            <div className="hero-art__spark hero-art__spark--two">✳</div>
            <div className="book book--back">
              <span className="book__spine" />
              <span className="book__title">READ<br />AND BEGIN</span>
              <span className="book__ornament">✳</span>
            </div>
            <div className="book book--middle">
              <span className="book__spine" />
              <span className="book__title">A FIELD<br />OF IDEAS</span>
              <span className="book__ornament">✳</span>
            </div>
            <div className="book book--front">
              <span className="book__spine" />
              <span className="book__title">STORIES<br />TO STAY</span>
              <span className="book__ornament">✳</span>
            </div>
            <div className="hero-art__caption">A good book makes room for possibility.</div>
          </div>
          <span aria-hidden="true" className="hero__index">
            01 — 03
          </span>
        </section>

        <section aria-labelledby="discover-title" className="intro" id="discover">
          <p className="eyebrow">A slower kind of scroll</p>
          <h2 id="discover-title">Good things are taking shape.</h2>
          <p>
            We’re making a considered place to discover books and the ideas inside them. Come back
            soon to explore the PUSTORA collection.
          </p>
        </section>

        <section aria-labelledby="story-title" className="story" id="our-story">
          <div className="story__ornament" aria-hidden="true">
            <span>p</span>
          </div>
          <div>
            <p className="eyebrow">A note from PUSTORA</p>
            <h2 id="story-title">Every great journey starts with a page.</h2>
            <p>
              We believe books can open doors, bring people closer, and make the everyday feel a
              little more meaningful. That belief is at the heart of everything we publish.
            </p>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <Link aria-label="PUSTORA home" className="brand brand--footer" to="/">
          <span aria-hidden="true" className="brand__mark">
            p
          </span>
          <span>pustora</span>
        </Link>
        <p>Stories to stay with you.</p>
        <span>© {new Date().getFullYear()} PUSTORA</span>
      </footer>
    </div>
  );
}
