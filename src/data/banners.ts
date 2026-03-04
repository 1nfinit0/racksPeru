// src/data/banners.ts

export interface Banner {
  id: number;
  imageUrl: string;
  linkUrl: string;
  altText: string;
  text: string;}

const banners: Banner[] = [
  {
    id: 0,
    imageUrl: '/banners/1.png',
    linkUrl: '',
    altText: 'Elegancia, confianza y durabilidad.',
    text: 'Racks del Perú',
  },
  {
    id: 1,
    imageUrl: '/banners/2.png',
    linkUrl: '',
    altText: 'Más de 250 clientes satisfechos en todo el Perú',
    text: 'Racks del Perú',
  },
  {
    id: 2,
    imageUrl: '/banners/3.png',
    linkUrl: '',
    altText: 'Racks del Perú, tu mejor opción en racks y accesorios',
    text: 'Racks del Perú',
  },
  {
    id: 3,
    imageUrl: '/banners/4.png',
    linkUrl: '',
    altText: 'Racks del Perú, calidad y servicio que superan tus expectativas',
    text: 'Racks del Perú',
  }
  // {
  //   id: 2,
  //   imageUrl: '/banners/2.webp',
  //   linkUrl: '',
  //   altText: 'Promotional Banner 2',
  // },  
  // {
  //   id: 3,
  //   imageUrl: '/banners/3.webp',
  //   linkUrl: '',
  //   altText: 'Promotional Banner 3',
  // },
  // {
  //   id: 4,
  //   imageUrl: '/banners/4.webp',
  //   linkUrl: '',
  //   altText: 'Promotional Banner 4',
  // },
  // {
  //   id: 5,
  //   imageUrl: '/banners/5.webp',
  //   linkUrl: '',
  //   altText: 'Promotional Banner 5',
  // }
];

export function getBanners(): Banner[] {
  return banners;
}