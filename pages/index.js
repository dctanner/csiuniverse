import { useState, useEffect } from 'react'
import Head from 'next/head'
import Image from 'next/image'
import { Inter } from '@next/font/google'
import styles from '../styles/Home.module.css'
import Tree from '../components/Tree'

const inter = Inter({ subsets: ['latin'] })

export async function getServerSideProps() {
  // Fetch data from external API
  const res = await fetch('https://sheetdb.io/api/v1/g43pocu1iyddf')
  const data = await res.json()

  // Pass data to the page via props
  return { props: { data } }
}

export default function Home({ data }) {

  // data is an array of objects with the following keys: Group, Company Name. Reorganise the data into a tree structure with the keys: name, children.
  const treeData = {
    name: 'Constellation Software',
    children: data.reduce((acc, { Group, 'Company Name': name }) => {
      const [parent, child] = Group.split(' > ');
      const parentIndex = acc.findIndex(({ name }) => name === parent);
      if (parentIndex === -1) {
        acc.push({
          name: parent,
          children: [{ name: child, children: [{ name }] }]
        })
      } else {
        const childIndex = acc[parentIndex].children.findIndex(({ name }) => name === child);
        if (childIndex === -1) {
          acc[parentIndex].children.push({ name: child, children: [{ name }] })
        } else {
          acc[parentIndex].children[childIndex].children.push({ name })
        }
      }
      return acc;
    }, [])
  }

  return (
    <>
      <Head>
        <title>Constellation Software Universe</title>
        <meta name="description" content="Tracking and visualising Constellation Software" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className={styles.main}>
        <h1 className={styles.title}>Constellation Software Universe</h1>
        <div className="">
          <Tree data={treeData} />
        </div>
      </main>
    </>
  )
}
