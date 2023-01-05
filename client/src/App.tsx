import Content from './views/Content';
import Header from './components/Header';
import Footer from './components/Footer';
import { MantineProvider } from '@mantine/core';
import { TypographyStylesProvider } from '@mantine/core';

function App() {
  return (
    <MantineProvider>
      <TypographyStylesProvider>
        <Header />
        <Content />
        {/* <Footer /> */}
      </TypographyStylesProvider>
    </MantineProvider>
  );
}

export default App;