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

  // data is an array of objects with the following keys: name, parent. Write a function that calls itself, to reformat the data into a recursive structure with the keys: name, children. Children is an array of objects with the same structure. The function should be called with the root node as an argument.
  function reformatData(data, root) {
    // create an empty children array for the root node
    root.children = [];
  
    // if root.name is not blank
    if (root.name) {
      // find all the children of the root node
      console.log(root.name)
      const children = data.filter(item => item.parent === root.name);
    
      // for each child, call the function recursively with the child as the root node
      children.forEach(child => {
        root.children.push(reformatData(data, child));
      });
    }
    // return the root node with the children array
    return root;
  }
  const rootNode = { name: "Constellation Software", children: [] };
  const treeData = reformatData(data, rootNode);
  // log the treeData to the console as a string
  console.log(JSON.stringify(treeData));

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
