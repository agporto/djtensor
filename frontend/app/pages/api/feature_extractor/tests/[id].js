import axios from 'axios';

export default async function handler(req, res) {
  const { id } = req.query;
  const baseUrl = process.env.DJANGO_API_BASE_URL;  

  const url = `${baseUrl}/api/feature_extractor/tests/${id}`;

  switch (req.method) {
    case 'GET':
      try {
        const response = await axios.get(url);
        const data = response.data;
        res.status(200).json(data);
      } catch (error) {
        console.error('Failed to fetch training test:', error);
        res.status(500).json({ message: 'Failed to fetch test' });
      }
      break;


    case 'DELETE':
      try {
        const { id } = req.query;  
        if (!id) {
          return res.status(400).json({ message: 'Missing ID for deletion' });
        }
        await axios.get(url);
        res.status(204).end();  
      } catch (error) {
        console.error('Failed to delete training tests:', error);
        res.status(500).json({ message: 'Failed to delete tests' });
      }
      break;

    default:
      res.setHeader('Allow', ['GET', 'DELETE']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
