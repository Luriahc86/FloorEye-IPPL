import api from "./api";

export const detectImage = async (imageBase64: string) => {
  const res = await api.post("/detection", {
    image: imageBase64,
  });
  return res.data;
};
